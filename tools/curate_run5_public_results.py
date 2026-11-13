"""Create aggregate-only public artifacts from the private Run5 output."""

import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import shutil
import statistics
import tempfile
from pathlib import Path


METRIC_COLUMNS = (
    "configuration", "val_macro_f1", "val_macro_f1_sd", "test_macro_f1",
    "test_macro_f1_sd", "test_accuracy", "test_accuracy_sd",
    "complaint_precision", "complaint_recall", "complaint_f1",
)
SEED_COLUMNS = (
    "seed", "best_epoch", "gpu", "val_macro_f1", "test_macro_f1",
    "test_accuracy", "complaint_precision", "complaint_recall",
    "complaint_f1", "wall_seconds", "peak_vram_mib",
)
DOMAIN_COLUMNS = (
    "model", "seed", "domain", "n", "macro_f1", "accuracy",
    "complaint_precision", "complaint_recall", "complaint_f1",
    "tn", "fp", "fn", "tp",
)
LEARNING_CURVE_COLUMNS = (
    "train_fraction", "train_size", "repetitions", "val_macro_f1_mean",
    "val_macro_f1_sd_sample",
)
SEQUENCE_COLUMNS = (
    "split", "n_examples", "includes_special_tokens", "max_input_tokens",
    "examples_truncated", "truncated_percent", "median_tokens",
    "p95_tokens", "max_tokens_before_truncation",
)
EXPECTED_MARKDOWN_CELL_SHA256 = {
    0: "62f6efc6b5dd1fe3714bb734d1f6515582eac7eac6b22ac3ab20e650188235b9",
    2: "602122d4921e79b67ca2124f406ee3690130d494ab219af693e041ffa1043ade",
    11: "3639515c9be901adf7898f6188fb7a65b6d7518d2c9f8554909b39a7cba39af6",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_keys(value, keys, context):
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a JSON object.")
    missing = set(keys) - set(value)
    if missing:
        raise ValueError(f"{context} is missing required keys: {sorted(missing)}")


def require_columns(rows, columns, context):
    if not rows:
        raise ValueError(f"{context} contains no rows.")
    required = set(columns)
    for index, row in enumerate(rows, start=1):
        missing = required - set(row)
        if missing:
            raise ValueError(
                f"{context} row {index} is missing required columns: {sorted(missing)}"
            )


def require_binary(rows, column, context):
    invalid_count = sum(row[column] not in {"0", "1"} for row in rows)
    if invalid_count:
        raise ValueError(
            f"{context} column {column!r} contains {invalid_count} non-binary values; contents redacted."
        )


def paths_overlap(left, right):
    left = os.path.normcase(str(left.resolve()))
    right = os.path.normcase(str(right.resolve()))
    try:
        common = os.path.normcase(os.path.commonpath((left, right)))
    except ValueError:
        return False
    return common in {left, right}


def normalize_utc_timestamp(value):
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as error:
        raise ValueError(
            "Kernel run time must be ISO-8601 with a UTC offset, e.g. "
            "2026-11-13T08:03:14Z."
        ) from error
    if parsed.tzinfo is None:
        raise ValueError("Kernel run time must include a UTC offset.")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def publish_staged(staging_dir, output_dir, names, force):
    output_dir.mkdir(parents=True, exist_ok=True)
    staged_paths = [staging_dir / name for name in names]
    if any(not path.is_file() for path in staged_paths):
        raise FileNotFoundError(
            "Staging directory does not contain every expected public artifact."
        )
    destinations = [output_dir / name for name in names]
    non_file_conflicts = [path for path in destinations if path.exists() and not path.is_file()]
    if non_file_conflicts:
        raise IsADirectoryError(
            f"Public artifact destination is not a file: {non_file_conflicts[0]}"
        )
    existing = [path for path in destinations if path.exists()]
    if existing and not force:
        raise FileExistsError(
            "A curated Run5 public artifact already exists; use --force to replace it."
        )

    backup_dir = Path(tempfile.mkdtemp(
        prefix=f".{output_dir.name}.run5-backup-", dir=output_dir.parent
    ))
    backed_up, installed = [], []
    try:
        for name, destination in zip(names, destinations):
            if destination.exists():
                backed_up.append(name)
                os.replace(destination, backup_dir / name)
            installed.append(name)
            os.replace(staging_dir / name, destination)
    except BaseException as commit_error:
        rollback_errors = []
        for name in reversed(installed):
            try:
                (output_dir / name).unlink(missing_ok=True)
            except BaseException as error:
                rollback_errors.append(error)
        for name in reversed(backed_up):
            try:
                backup = backup_dir / name
                if backup.exists():
                    os.replace(backup, output_dir / name)
            except BaseException as error:
                rollback_errors.append(error)
        if rollback_errors:
            details = "; ".join(type(error).__name__ for error in rollback_errors)
            raise RuntimeError(
                f"Run5 publication failed and rollback was incomplete ({details}); "
                f"preserve backup directory: {backup_dir}"
            ) from commit_error
        shutil.rmtree(backup_dir)
        raise
    shutil.rmtree(backup_dir)


def sha256_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def notebook_cells(path):
    notebook = read_json(path)
    return notebook, ["".join(cell.get("source", [])) for cell in notebook["cells"]]


def source_hash(path, code_only=False):
    notebook, sources = notebook_cells(path)
    selected = [
        {"cell_type": cell.get("cell_type"), "source": source}
        for cell, source in zip(notebook["cells"], sources)
        if not code_only or cell.get("cell_type") == "code"
    ]
    canonical = json.dumps(selected, ensure_ascii=False, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))


class StripDocstrings(ast.NodeTransformer):
    @staticmethod
    def strip(body):
        if body and isinstance(body[0], ast.Expr):
            value = body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return body[1:]
        return body

    def visit_Module(self, node):
        node.body = self.strip(node.body)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        node.body = self.strip(node.body)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        node.body = self.strip(node.body)
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        node.body = self.strip(node.body)
        return self.generic_visit(node)


def functional_ast_hash(path):
    notebook, _ = notebook_cells(path)
    trees = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        normalized = "\n".join(
            "pass  # notebook magic" if line.lstrip().startswith(("%", "!")) else line
            for line in source.splitlines()
        )
        tree = StripDocstrings().visit(ast.parse(normalized))
        ast.fix_missing_locations(tree)
        trees.append(ast.dump(tree, include_attributes=False))
    return sha256_bytes("\n".join(trees).encode("utf-8"))


def assert_documentation_only(execution_notebook, published_notebook):
    execution, execution_sources = notebook_cells(execution_notebook)
    published, published_sources = notebook_cells(published_notebook)
    if len(execution_sources) != len(published_sources):
        raise ValueError("Published notebook cell count differs from the executed source.")

    old_docstring = '"""Run the UIT-ViOCD complaint detection experiment on CPU."""'
    new_docstring = '"""Prepare splits and evaluate CPU-based classical baselines."""'
    code_changes = []
    markdown_changes = []
    for index, (left, right) in enumerate(zip(execution["cells"], published["cells"])):
        left_source, right_source = execution_sources[index], published_sources[index]
        if left.get("cell_type") != right.get("cell_type"):
            raise ValueError("Published notebook changes a cell type.")
        if left.get("cell_type") == "code" and left_source != right_source:
            code_changes.append((index, left_source, right_source))
        elif left.get("cell_type") != "code" and left_source != right_source:
            if left.get("cell_type") != "markdown":
                raise ValueError("Published notebook changes a non-markdown, non-code cell.")
            markdown_changes.append(index)
    if markdown_changes != list(EXPECTED_MARKDOWN_CELL_SHA256):
        raise ValueError("Published notebook Markdown changes differ from the reviewed cells.")
    for index, expected_hash in EXPECTED_MARKDOWN_CELL_SHA256.items():
        actual_hash = sha256_bytes(published_sources[index].encode("utf-8"))
        if actual_hash != expected_hash:
            raise ValueError(f"Published notebook Markdown cell {index} differs from the reviewed text.")
    if len(code_changes) != 1:
        raise ValueError("Expected only the CPU-baseline docstring to change in code cells.")
    _, before, after = code_changes[0]
    if old_docstring not in before or before.replace(old_docstring, new_docstring, 1) != after:
        raise ValueError("Published executable-cell edit is not the reviewed docstring correction.")


def write_csv(path, rows, columns):
    require_columns(rows, columns, path.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_split_summary(summary):
    require_keys(summary, ("selected", "data", "segmented_overlap_audit"), "Run5 summary")
    data = summary["data"]
    require_keys(data, ("train", "val", "test", "source_train_pool", "split_protocol"),
                 "Run5 summary data")
    split_keep = (
        "retained", "labels", "domains", "whitespace_units", "median_length", "p95_length",
    )
    splits = {}
    for name in ("train", "val", "test"):
        require_keys(data[name], split_keep, f"Run5 {name} split summary")
        splits[name] = {key: data[name][key] for key in split_keep}
    pool_keep = (
        "raw", "missing", "blank", "conflict_rows", "duplicate_rows", "overlap_rows",
        "retained", "labels", "domains", "whitespace_units", "median_length", "p95_length",
    )
    require_keys(data["source_train_pool"], pool_keep, "Run5 source train pool summary")
    pool = {key: data["source_train_pool"][key] for key in pool_keep}
    protocol = data["split_protocol"]
    protocol_keep = (
        "source_partition", "source_pool_rows", "split_seed", "second_split_seed",
        "requested_ratio", "stratification", "actual_counts",
        "legacy_validation_test_use", "segmented_pool_unique",
    )
    require_keys(protocol, (*protocol_keep, "private_manifest_sha256"), "Run5 split protocol")
    segmented_keep = (
        "split", "rows", "within_split_duplicate_segmented_rows",
        "cross_split_segmented_overlap_rows", "within_split_segment_label_conflict_rows",
        "cross_split_segment_label_conflict_rows",
    )
    audit = summary["segmented_overlap_audit"]
    if not isinstance(audit, list) or len(audit) != 3:
        raise ValueError("Run5 segmented overlap audit must contain exactly three split rows.")
    for index, row in enumerate(audit, start=1):
        require_keys(row, segmented_keep, f"Run5 segmented overlap audit row {index}")
    if {row["split"] for row in audit} != {"train", "val", "test"}:
        raise ValueError(
            "Run5 segmented overlap audit must cover train, val, and test exactly once."
        )
    return {
        "selected_baseline_by_validation": summary["selected"],
        "splits": splits,
        "cleaned_original_train_pool": pool,
        "split_protocol": {key: protocol[key] for key in protocol_keep},
        "segmented_overlap_audit": [
            {key: row[key] for key in segmented_keep}
            for row in summary["segmented_overlap_audit"]
        ],
    }


def confusion_rows(output_dir):
    baseline_path = output_dir / "results" / "baseline_all_test_predictions.csv"
    baseline = read_csv(baseline_path)
    require_columns(baseline, ("test_row", "label", "domain"), baseline_path.name)
    prediction_columns = [
        key for key in baseline[0]
        if key.startswith("prediction_") and key not in {"prediction_seed_42", "prediction_seed_43", "prediction_seed_44"}
    ]
    if not prediction_columns:
        raise ValueError("No baseline prediction columns were found.")
    for column in ("test_row", "label", "domain"):
        if any(not (row[column] or "").strip() for row in baseline):
            raise ValueError(f"Baseline test predictions contain blank {column!r} values.")
    baseline_ids = [row["test_row"] for row in baseline]
    if len(set(baseline_ids)) != len(baseline_ids):
        raise ValueError("Baseline test predictions contain duplicate test_row IDs.")
    require_binary(baseline, "label", baseline_path.name)
    for column in prediction_columns:
        require_binary(baseline, column, baseline_path.name)
    rows = []

    def append_counts(name, seed, records, prediction_column):
        tn = fp = fn = tp = 0
        for record in records:
            label, prediction = int(record["label"]), int(record[prediction_column])
            tn += label == 0 and prediction == 0
            fp += label == 0 and prediction == 1
            fn += label == 1 and prediction == 0
            tp += label == 1 and prediction == 1
        rows.append({
            "configuration": name, "seed": seed, "n": tn + fp + fn + tp,
            "tn": tn, "fp": fp, "fn": fn, "tp": tp,
        })

    for column in prediction_columns:
        append_counts(column.removeprefix("prediction_"), "", baseline, column)
    for seed in (42, 43, 44):
        seed_path = output_dir / "results_phobert" / f"seed_{seed}" / "phobert_predictions.csv"
        records = read_csv(seed_path)
        require_columns(records, ("test_row", "label", "domain", "prediction"), seed_path.name)
        if len(records) != len(baseline):
            raise ValueError(
                f"PhoBERT seed {seed} has {len(records)} rows; expected {len(baseline)}."
            )
        for column in ("test_row", "label", "domain"):
            if [row[column] for row in records] != [row[column] for row in baseline]:
                raise ValueError(
                    f"PhoBERT seed {seed} does not align with baseline {column} values/order."
                )
        seed_ids = [row["test_row"] for row in records]
        if len(set(seed_ids)) != len(seed_ids):
            raise ValueError(f"PhoBERT seed {seed} contains duplicate test_row IDs.")
        require_binary(records, "label", seed_path.name)
        require_binary(records, "prediction", seed_path.name)
        append_counts("D_PhoBERT", seed, records, "prediction")
    return rows


def validate_run_metadata(summary, paired, split_manifest, seed_metrics, checkpoint, environment):
    require_keys(paired, (
        "baseline_configuration", "test_rows", "baseline_macro_f1",
        "phobert_mean_seed_macro_f1", "observed_mean_difference",
        "paired_bootstrap_ci95", "bootstrap_samples", "seeds", "interpretation",
    ), "Run5 paired comparison")
    require_keys(split_manifest, (
        "dataset_commit", "source_csv_sha256", "cleaned_pool_rows", "cleaning_audit",
        "split_seed", "second_split_seed", "requested_ratio", "stratification",
        "actual_counts",
    ), "Run5 split manifest")
    require_keys(environment, (
        "cuda_available", "cuda_runtime", "gpu", "dataset_commit", "model",
        "model_revision", "seeds",
    ), "Run5 environment")
    if environment["cuda_available"] is not True or not str(environment["gpu"]).strip():
        raise ValueError("Run5 environment does not confirm an active GPU.")
    if environment["dataset_commit"] != split_manifest["dataset_commit"]:
        raise ValueError("Run5 environment and split manifest use different dataset commits.")

    data = summary["data"]
    protocol = data["split_protocol"]
    manifest_digest = sha256_bytes(
        json.dumps(
            split_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )
    if protocol["private_manifest_sha256"] != manifest_digest:
        raise ValueError("Run5 summary and split manifest hashes do not match.")
    if protocol["actual_counts"] != split_manifest["actual_counts"]:
        raise ValueError("Run5 summary and split manifest contain different split counts.")
    retained_counts = {
        name: data[name]["retained"] for name in ("train", "val", "test")
    }
    if protocol["actual_counts"] != retained_counts:
        raise ValueError("Run5 split counts differ from retained counts in the summary.")
    if sum(retained_counts.values()) != split_manifest["cleaned_pool_rows"]:
        raise ValueError("Run5 split counts do not sum to the cleaned pool size.")
    if protocol["source_pool_rows"] != split_manifest["cleaned_pool_rows"]:
        raise ValueError("Run5 summary and split manifest contain different source-pool sizes.")
    if protocol["split_seed"] != split_manifest["split_seed"]:
        raise ValueError("Run5 summary and split manifest use different split seeds.")
    if protocol["second_split_seed"] != split_manifest["second_split_seed"]:
        raise ValueError("Run5 summary and split manifest use different second split seeds.")
    if protocol["requested_ratio"] != split_manifest["requested_ratio"]:
        raise ValueError("Run5 summary and split manifest use different requested split ratios.")
    if protocol["stratification"] != split_manifest["stratification"]:
        raise ValueError("Run5 summary and split manifest use different stratification rules.")
    if data["source_train_pool"] != split_manifest["cleaning_audit"]:
        raise ValueError("Run5 summary and split manifest contain different cleaning audits.")
    if data["source_train_pool"]["retained"] != split_manifest["cleaned_pool_rows"]:
        raise ValueError("Run5 cleaning audit retained count differs from the manifest pool size.")
    expected_test_rows = data["test"]["retained"]
    if paired["test_rows"] != expected_test_rows:
        raise ValueError("Run5 paired comparison row count differs from the test split summary.")
    if paired["baseline_configuration"] != summary["selected"]:
        raise ValueError("Run5 selected baseline differs between summary and paired comparison.")

    expected_seeds = (42, 43, 44)
    for name, values in (
        ("environment", environment["seeds"]),
        ("paired comparison", paired["seeds"]),
    ):
        try:
            actual = tuple(int(value) for value in values)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Run5 {name} has invalid seed values.") from error
        if actual != expected_seeds:
            raise ValueError(f"Run5 {name} seeds must be {expected_seeds}, got {actual}.")

    require_columns(seed_metrics, SEED_COLUMNS, "Run5 seed metrics")
    if len(seed_metrics) != len(expected_seeds):
        raise ValueError("Run5 seed metrics must contain exactly three rows.")
    try:
        metric_seeds = tuple(int(row["seed"]) for row in seed_metrics)
    except (TypeError, ValueError) as error:
        raise ValueError("Run5 seed metrics contain invalid seed values.") from error
    if metric_seeds != expected_seeds:
        raise ValueError(f"Run5 seed metrics must contain seeds {expected_seeds} in order.")

    if not isinstance(checkpoint, list) or len(checkpoint) != len(expected_seeds):
        raise ValueError("Run5 checkpoint verification must contain exactly three seed rows.")
    require_columns(checkpoint, (
        "seed", "test_rows", "predictions_identical_to_saved", "base_model_revision",
    ), "Run5 checkpoint verification")
    checkpoint_seeds = tuple(int(row["seed"]) for row in checkpoint)
    if checkpoint_seeds != expected_seeds:
        raise ValueError(
            f"Run5 checkpoint verification must contain seeds {expected_seeds} in order."
        )
    for row in checkpoint:
        if row["test_rows"] != expected_test_rows:
            raise ValueError(
                f"Run5 checkpoint seed {row['seed']} has an unexpected test row count."
            )
        if row["predictions_identical_to_saved"] is not True:
            raise ValueError(f"Run5 checkpoint seed {row['seed']} did not reproduce saved predictions.")
        if row["base_model_revision"] != environment["model_revision"]:
            raise ValueError(f"Run5 checkpoint seed {row['seed']} uses a different model revision.")


def confusion_metrics(row):
    tn, fp, fn, tp = (int(row[key]) for key in ("tn", "fp", "fn", "tp"))
    total = tn + fp + fn + tp
    if total != int(row["n"]) or total == 0:
        raise ValueError("Confusion counts do not sum to a positive row count.")
    positive_f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    negative_f1 = 2 * tn / (2 * tn + fp + fn) if 2 * tn + fp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "test_macro_f1": (positive_f1 + negative_f1) / 2,
        "test_accuracy": (tn + tp) / total,
        "complaint_precision": precision,
        "complaint_recall": recall,
        "complaint_f1": positive_f1,
    }


def require_metric_match(actual, expected, context, metric):
    try:
        actual_value, expected_value = float(actual), float(expected)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{context} has a non-numeric {metric} value.") from error
    if not math.isclose(actual_value, expected_value, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(
            f"{context} {metric} mismatch: metrics={actual_value}, confusion={expected_value}."
        )


def validate_metrics_against_confusion(comparison_rows, seed_metrics, confusion_count_rows, paired):
    comparison_by_name = {row["configuration"]: row for row in comparison_rows}
    if len(comparison_by_name) != len(comparison_rows):
        raise ValueError("Run5 comparison metrics contain duplicate configurations.")
    seed_metrics_by_seed = {int(row["seed"]): row for row in seed_metrics}
    counts_by_baseline = {
        row["configuration"]: row for row in confusion_count_rows if row["seed"] == ""
    }
    counts_by_seed = {
        int(row["seed"]): row for row in confusion_count_rows if row["seed"] != ""
    }
    for configuration, counts in counts_by_baseline.items():
        if configuration not in comparison_by_name:
            raise ValueError(f"Missing metric row for baseline {configuration}.")
        calculated = confusion_metrics(counts)
        for metric, value in calculated.items():
            require_metric_match(
                comparison_by_name[configuration][metric], value,
                f"Baseline {configuration}", metric,
            )
    for seed, counts in counts_by_seed.items():
        if seed not in seed_metrics_by_seed:
            raise ValueError(f"Missing seed metrics for PhoBERT seed {seed}.")
        calculated = confusion_metrics(counts)
        for metric, value in calculated.items():
            require_metric_match(
                seed_metrics_by_seed[seed][metric], value,
                f"PhoBERT seed {seed}", metric,
            )

    if set(counts_by_seed) != {42, 43, 44}:
        raise ValueError("Run5 confusion counts must include PhoBERT seeds 42, 43, and 44 exactly.")
    mean_rows = [row for name, row in comparison_by_name.items() if name not in counts_by_baseline]
    if len(mean_rows) != 1:
        raise ValueError("Run5 comparison metrics must contain exactly one PhoBERT mean row.")
    for metric in (
        "val_macro_f1", "test_macro_f1", "test_accuracy",
        "complaint_precision", "complaint_recall", "complaint_f1",
    ):
        expected_mean = sum(float(seed_metrics_by_seed[seed][metric]) for seed in (42, 43, 44)) / 3
        require_metric_match(
            mean_rows[0][metric], expected_mean, "Run5 PhoBERT mean row", metric,
        )
    for metric, spread in (
        ("val_macro_f1", "val_macro_f1_sd"),
        ("test_macro_f1", "test_macro_f1_sd"),
        ("test_accuracy", "test_accuracy_sd"),
    ):
        expected_spread = statistics.stdev(
            float(seed_metrics_by_seed[seed][metric]) for seed in (42, 43, 44)
        )
        require_metric_match(
            mean_rows[0][spread], expected_spread, "Run5 PhoBERT mean row", spread,
        )
    selected = paired["baseline_configuration"]
    if selected not in counts_by_baseline:
        raise ValueError(f"Selected baseline {selected} has no confusion-count row.")
    validation_scores = {
        name: float(comparison_by_name[name]["val_macro_f1"])
        for name in counts_by_baseline
    }
    if any(not math.isfinite(score) for score in validation_scores.values()):
        raise ValueError("Run5 baseline validation Macro-F1 values must be finite.")
    best_validation_macro_f1 = max(validation_scores.values())
    if validation_scores[selected] < best_validation_macro_f1 - 1e-12:
        raise ValueError(f"Selected baseline {selected} is not the validation Macro-F1 maximum.")
    require_metric_match(
        paired["baseline_macro_f1"], confusion_metrics(counts_by_baseline[selected])["test_macro_f1"],
        "Run5 paired comparison baseline", "test_macro_f1",
    )
    mean_seed_f1 = sum(float(seed_metrics_by_seed[seed]["test_macro_f1"]) for seed in (42, 43, 44)) / 3
    require_metric_match(
        paired["phobert_mean_seed_macro_f1"], mean_seed_f1,
        "Run5 paired comparison PhoBERT mean", "test_macro_f1",
    )
    require_metric_match(
        paired["observed_mean_difference"],
        mean_seed_f1 - float(paired["baseline_macro_f1"]),
        "Run5 paired comparison difference", "observed_mean_difference",
    )


def compact_robustness(output_dir):
    robustness = read_json(output_dir / "results_phobert" / "robustness_summary.json")
    uncertainty = read_json(output_dir / "results_robustness" / "accent_augmentation_uncertainty.json")
    augmentation = read_json(output_dir / "results_robustness" / "accent_augmentation.json")
    require_keys(robustness, (
        "seeds", "test_unaccented_rows", "accent_overlap_rows", "sensitivity_rows",
        "metrics", "interpretation",
    ), "Run5 robustness summary")
    try:
        robustness_seeds = tuple(int(seed) for seed in robustness["seeds"])
    except (TypeError, ValueError) as error:
        raise ValueError("Run5 robustness summary has invalid seed values.") from error
    if robustness_seeds != (42, 43, 44):
        raise ValueError(f"Run5 robustness seeds must be (42, 43, 44), got {robustness_seeds}.")
    metric_names = (
        "clean_test_macro_f1", "unaccented_test_macro_f1",
        "unaccented_test_accuracy", "sensitivity_macro_f1",
        "challenge_pairs_correct",
    )
    require_keys(robustness["metrics"], metric_names, "Run5 robustness metrics")
    if not isinstance(augmentation, list) or not augmentation:
        raise ValueError("Run5 accent augmentation summary must contain model rows.")
    augmentation_columns = (
        "model", "training_rows", "val_clean", "val_unaccented", "test_clean",
        "test_unaccented", "test_unaccented_sensitivity", "sensitivity_test_n",
        "accent_overlap_test_n",
    )
    for index, row in enumerate(augmentation, start=1):
        require_keys(row, augmentation_columns, f"Run5 accent augmentation row {index}")
    if len({row["model"] for row in augmentation}) != len(augmentation):
        raise ValueError("Run5 accent augmentation contains duplicate model rows.")
    if not isinstance(uncertainty, dict) or not uncertainty:
        raise ValueError("Run5 accent augmentation uncertainty must contain intervals.")
    interval_columns = (
        "test_rows", "macro_f1_difference", "bootstrap_difference_ci95",
        "bootstrap_samples", "correct_difference",
    )
    for name, item in uncertainty.items():
        require_keys(item, interval_columns, f"Run5 uncertainty interval {name}")
    augmentation_metrics = {
        row["model"]: {k: row[k] for k in (
            "training_rows", "val_clean", "val_unaccented", "test_clean",
            "test_unaccented", "test_unaccented_sensitivity",
            "sensitivity_test_n", "accent_overlap_test_n",
        )}
        for row in augmentation
    }
    intervals = {
        key: {k: item[k] for k in (
            "test_rows", "macro_f1_difference", "bootstrap_difference_ci95",
            "bootstrap_samples", "correct_difference",
        ) if k in item}
        for key, item in uncertainty.items()
    }
    metrics = {name: robustness["metrics"][name] for name in metric_names}
    return {
        "phobert": {
            "seeds": robustness["seeds"],
            "test_unaccented_rows": robustness["test_unaccented_rows"],
            "accent_overlap_rows": robustness["accent_overlap_rows"],
            "sensitivity_rows": robustness["sensitivity_rows"],
            "metrics": metrics,
        },
        "accent_augmentation": {
            "models": augmentation_metrics,
            "paired_uncertainty": intervals,
            "interpretation": "Synthetic accent-removal robustness test; not natural unaccented data.",
        },
        "synthetic_diagnostic_pairs": robustness["metrics"]["challenge_pairs_correct"],
        "interpretation": robustness["interpretation"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execution-source", type=Path, required=True)
    parser.add_argument("--pulled-source", type=Path, required=True)
    parser.add_argument("--published-notebook", type=Path, required=True)
    parser.add_argument(
        "--kernel-last-run-utc", required=True,
        help="Kaggle run time in ISO-8601 form with an explicit UTC offset.",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    input_dir = args.input_dir.resolve(strict=True)
    publication_dir = args.output_dir.resolve(strict=False)
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Run5 input path is not a directory: {input_dir}")
    if paths_overlap(input_dir, publication_dir):
        raise ValueError("Run5 input and public output directories must not overlap.")
    if publication_dir.exists() and not publication_dir.is_dir():
        raise NotADirectoryError(f"Public output path is not a directory: {publication_dir}")
    kernel_last_run_utc = normalize_utc_timestamp(args.kernel_last_run_utc)
    output_dir = input_dir
    expected = (
        output_dir / "results" / "summary.json",
        output_dir / "results" / "metrics.csv",
        output_dir / "results" / "baseline_all_test_predictions.csv",
        output_dir / "results_phobert" / "comparison.csv",
        output_dir / "results_phobert" / "seed_metrics.csv",
        output_dir / "results_phobert" / "paired_bootstrap.json",
        output_dir / "results_phobert" / "per_domain_metrics.csv",
        output_dir / "results" / "learning_curve_summary.csv",
        output_dir / "results_phobert" / "sequence_length_audit.csv",
        output_dir / "results_phobert" / "environment.json",
        output_dir / "results_phobert" / "checkpoint_restore_verification.json",
        output_dir / "results_phobert" / "robustness_summary.json",
        output_dir / "results_robustness" / "accent_augmentation.json",
        output_dir / "results_robustness" / "accent_augmentation_uncertainty.json",
        output_dir / "results" / "split_manifest_private.json",
    )
    missing = [path.name for path in expected if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"A required Run5 aggregate artifact is missing: {missing}")

    notebooks = (args.execution_source, args.pulled_source, args.published_notebook)
    parsed = [notebook_cells(path)[0] for path in notebooks]
    if any(any(cell.get("outputs") for cell in notebook["cells"]) for notebook in parsed):
        raise ValueError("A source notebook contains saved outputs; public release refused.")
    code_sources = [
        ["".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code"]
        for notebook in parsed
    ]
    if code_sources[0] != code_sources[1]:
        raise ValueError("Submitted and Kaggle-pulled executable cells do not match.")
    assert_documentation_only(args.execution_source, args.published_notebook)
    functional_hashes = [functional_ast_hash(path) for path in notebooks]
    if len(set(functional_hashes)) != 1:
        raise ValueError("Published notebook changes executable logic; public curation refused.")

    names = (
        "run5_train_holdout_model_metrics.csv",
        "run5_train_holdout_seed_metrics.csv",
        "run5_train_holdout_domain_metrics.csv",
        "run5_train_holdout_learning_curve.csv",
        "run5_train_holdout_sequence_length.csv",
        "run5_train_holdout_confusion_counts.csv",
        "run5_train_holdout_summary.json",
        "run5_train_holdout_robustness.json",
        "run5_train_holdout_checkpoint_restore.json",
        "run5_train_holdout_environment.json",
        "run5_train_holdout_provenance.json",
    )
    destinations = [publication_dir / name for name in names]
    if not args.force and any(path.exists() for path in destinations):
        raise FileExistsError("A curated Run5 public artifact already exists; use --force to replace it.")
    publication_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = tempfile.TemporaryDirectory(
        prefix=f".{publication_dir.name}.run5-curation-", dir=publication_dir.parent
    )
    artifact_dir = Path(staging.name)

    comparison_rows = read_csv(output_dir / "results_phobert" / "comparison.csv")
    require_columns(comparison_rows, ("configuration",), "Run5 comparison metrics")
    seed_metrics = read_csv(output_dir / "results_phobert" / "seed_metrics.csv")
    domain_rows = read_csv(output_dir / "results_phobert" / "per_domain_metrics.csv")
    learning_curve_rows = read_csv(output_dir / "results" / "learning_curve_summary.csv")
    sequence_rows = read_csv(output_dir / "results_phobert" / "sequence_length_audit.csv")
    confusion_count_rows = confusion_rows(output_dir)

    summary = read_json(output_dir / "results" / "summary.json")
    paired = read_json(output_dir / "results_phobert" / "paired_bootstrap.json")
    split_manifest = read_json(output_dir / "results" / "split_manifest_private.json")
    split_manifest_path = output_dir / "results" / "split_manifest_private.json"
    checkpoint = read_json(output_dir / "results_phobert" / "checkpoint_restore_verification.json")
    environment = read_json(output_dir / "results_phobert" / "environment.json")
    summary_data_public = compact_split_summary(summary)
    validate_run_metadata(summary, paired, split_manifest, seed_metrics, checkpoint, environment)
    validate_metrics_against_confusion(
        comparison_rows, seed_metrics, confusion_count_rows, paired
    )
    if any(row["n"] != paired["test_rows"] for row in confusion_count_rows):
        raise ValueError("Confusion-count rows do not all match the paired-comparison test size.")
    metric_baselines = {
        row["configuration"] for row in comparison_rows
        if not row["configuration"].startswith("D_")
    }
    count_baselines = {
        row["configuration"] for row in confusion_count_rows if row["seed"] == ""
    }
    if metric_baselines != count_baselines or paired["baseline_configuration"] not in count_baselines:
        raise ValueError("Run5 comparison metrics and confusion counts do not cover the same baselines.")
    if summary_data_public["splits"]["test"]["retained"] != paired["test_rows"]:
        raise ValueError("Public test split summary differs from paired-comparison row count.")

    write_csv(artifact_dir / names[0], comparison_rows, METRIC_COLUMNS)
    write_csv(artifact_dir / names[1], seed_metrics, SEED_COLUMNS)
    write_csv(artifact_dir / names[2], domain_rows, DOMAIN_COLUMNS)
    write_csv(artifact_dir / names[3], learning_curve_rows, LEARNING_CURVE_COLUMNS)
    write_csv(artifact_dir / names[4], sequence_rows, SEQUENCE_COLUMNS)
    write_csv(artifact_dir / names[5], confusion_count_rows, ("configuration", "seed", "n", "tn", "fp", "fn", "tp"))
    summary_public = {
        "dataset_commit": split_manifest["dataset_commit"],
        "data_and_split": summary_data_public,
        "comparison": {k: paired[k] for k in (
            "baseline_configuration", "test_rows", "baseline_macro_f1",
            "phobert_mean_seed_macro_f1", "observed_mean_difference",
            "paired_bootstrap_ci95", "bootstrap_samples", "seeds", "interpretation",
        )},
        "evaluation_scope": "Post-hoc train-derived internal holdout; not independent confirmation.",
    }
    write_json(artifact_dir / names[6], summary_public)
    write_json(artifact_dir / names[7], compact_robustness(output_dir))

    checkpoint_public = [{k: row[k] for k in (
        "seed", "test_rows", "predictions_identical_to_saved",
        "base_model_revision", "max_length", "micro_batch",
    )} for row in checkpoint]
    write_json(artifact_dir / names[8], checkpoint_public)

    environment_public = {k: environment[k] for k in (
        "python", "platform", "packages", "cuda_available", "cuda_runtime",
        "gpu", "dataset_commit", "model", "model_revision", "seeds",
    )}
    write_json(artifact_dir / names[9], environment_public)

    artifacts = {name: sha256_file(artifact_dir / name) for name in names[:-1]}
    source_files = expected
    provenance = {
        "artifact_label": "run5_v5",
        "kernel": "hiptetsuya/viocd-phobert-fresh-holdout-run5",
        "kernel_status": "COMPLETE",
        "kernel_status_basis": "Manually verified in Kaggle; this curation script does not query live kernel status.",
        "kernel_last_run_utc": kernel_last_run_utc,
        "accelerator": environment["gpu"],
        "private_kernel": True,
        "downloaded_output_file_count": sum(1 for path in output_dir.rglob("*") if path.is_file()),
        "dataset_commit": split_manifest["dataset_commit"],
        "dataset_csv_sha256": split_manifest["source_csv_sha256"],
        "model": environment["model"],
        "model_revision": environment["model_revision"],
        "run5_split_manifest_sha256": sha256_file(split_manifest_path),
        "source_notebooks": {
            "execution_source_file_sha256": sha256_file(args.execution_source),
            "kaggle_pulled_source_file_sha256": sha256_file(args.pulled_source),
            "published_notebook_file_sha256": sha256_file(args.published_notebook),
            "curation_script_sha256": sha256_file(Path(__file__)),
            "execution_source_cell_sha256": source_hash(args.execution_source),
            "kaggle_pulled_source_cell_sha256": source_hash(args.pulled_source),
            "published_source_cell_sha256": source_hash(args.published_notebook),
            "execution_code_cell_sha256": source_hash(args.execution_source, code_only=True),
            "published_code_cell_sha256": source_hash(args.published_notebook, code_only=True),
            "source_cell_hash_method": "SHA-256 over canonical JSON of ordered cell-type/source entries, UTF-8 encoded.",
            "code_cell_hash_method": "SHA-256 over canonical JSON of ordered executable-cell type/source entries, UTF-8 encoded.",
            "submitted_and_pulled_code_cells_identical": code_sources[0] == code_sources[1],
            "functional_ast_sha256_docstrings_removed": functional_hashes[0],
            "functional_ast_hash_method": "AST dumps of executable cells after replacing Jupyter magic lines with pass and removing docstrings; cells joined with newline.",
            "published_functional_ast_matches_execution": functional_hashes[0] == functional_hashes[2],
            "published_notebook_contains_saved_outputs": False,
            "published_changes_are_documentation_only": True,
            "published_documentation_changes": {
                "markdown_cell_indices": list(EXPECTED_MARKDOWN_CELL_SHA256),
                "markdown_cell_sha256": EXPECTED_MARKDOWN_CELL_SHA256,
                "code_cell_change": "Cell 3 module docstring narrowed to CPU-based classical baselines.",
            },
        },
        "methodology_limitations": [
            "All Run5 partitions were drawn from the cleaned original-training pool; every row in that pool was previously used in Run4 supervised training.",
            "The same Run5 split was reused across versions v1-v5.",
            "A local preflight displayed partial text and source-row indices that can be linked to public labels; Run5 is not a blind independent confirmation.",
        ],
        "public_release": {
            "raw_review_text": False,
            "row_ids": False,
            "per_row_predictions": False,
            "model_checkpoints": False,
            "aggregate_artifacts_sha256": artifacts,
        },
        "curated_source_artifacts_sha256": {
            path.relative_to(output_dir).as_posix(): sha256_file(path)
            for path in source_files
        },
    }
    write_json(artifact_dir / names[10], provenance)
    publish_staged(artifact_dir, publication_dir, names, args.force)
    staging.cleanup()
    print(f"curated_artifacts={len(names)}; raw_rows_published=False; "
          f"functional_code_matches_execution={provenance['source_notebooks']['published_functional_ast_matches_execution']}; "
          f"test_rows={paired['test_rows']}; gpu={environment['gpu']}")


if __name__ == "__main__":
    main()
