"""Create aggregate-only public artifacts from the private Run5 output."""

import argparse
import ast
import csv
import hashlib
import json
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
    missing = set(columns) - (set(rows[0]) if rows else set())
    if missing:
        raise ValueError(f"Missing expected aggregate columns in {path.name}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in rows)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_split_summary(summary):
    keep = (
        "raw", "missing", "blank", "conflict_rows", "duplicate_rows",
        "overlap_rows", "retained", "labels", "domains", "whitespace_units",
        "median_length", "p95_length",
    )
    data = summary["data"]
    splits = {name: {k: data[name][k] for k in keep if k in data[name]}
              for name in ("train", "val", "test")}
    pool = {k: data["source_train_pool"][k] for k in keep if k in data["source_train_pool"]}
    protocol = data["split_protocol"]
    protocol_keep = (
        "source_partition", "source_pool_rows", "split_seed", "second_split_seed",
        "requested_ratio", "stratification", "actual_counts",
        "legacy_validation_test_use", "segmented_pool_unique",
    )
    segmented_keep = (
        "split", "rows", "within_split_duplicate_segmented_rows",
        "cross_split_segmented_overlap_rows", "within_split_segment_label_conflict_rows",
        "cross_split_segment_label_conflict_rows",
    )
    return {
        "selected_baseline_by_validation": summary["selected"],
        "splits": splits,
        "cleaned_original_train_pool": pool,
        "split_protocol": {k: protocol[k] for k in protocol_keep if k in protocol},
        "segmented_overlap_audit": [
            {k: row[k] for k in segmented_keep if k in row}
            for row in summary["segmented_overlap_audit"]
        ],
    }


def confusion_rows(output_dir):
    baseline = read_csv(output_dir / "results" / "baseline_all_test_predictions.csv")
    if not baseline:
        raise ValueError("Baseline test predictions are empty.")
    prediction_columns = [
        key for key in baseline[0]
        if key.startswith("prediction_") and key not in {"prediction_seed_42", "prediction_seed_43", "prediction_seed_44"}
    ]
    if not prediction_columns:
        raise ValueError("No baseline prediction columns were found.")
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
        records = read_csv(output_dir / "results_phobert" / f"seed_{seed}" / "phobert_predictions.csv")
        append_counts("D_PhoBERT", seed, records, "prediction")
    return rows


def compact_robustness(output_dir):
    robustness = read_json(output_dir / "results_phobert" / "robustness_summary.json")
    uncertainty = read_json(output_dir / "results_robustness" / "accent_augmentation_uncertainty.json")
    augmentation = read_json(output_dir / "results_robustness" / "accent_augmentation.json")
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
    metric_names = (
        "clean_test_macro_f1", "unaccented_test_macro_f1",
        "unaccented_test_accuracy", "sensitivity_macro_f1",
        "challenge_pairs_correct",
    )
    metrics = {
        name: robustness["metrics"][name]
        for name in metric_names if name in robustness["metrics"]
    }
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
    parser.add_argument("--kernel-last-run-utc", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output_dir = args.input_dir
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
    destinations = [args.output_dir / name for name in names]
    if not args.force and any(path.exists() for path in destinations):
        raise FileExistsError("A curated Run5 public artifact already exists; use --force to replace it.")

    write_csv(args.output_dir / names[0], read_csv(output_dir / "results_phobert" / "comparison.csv"), METRIC_COLUMNS)
    write_csv(args.output_dir / names[1], read_csv(output_dir / "results_phobert" / "seed_metrics.csv"), SEED_COLUMNS)
    write_csv(args.output_dir / names[2], read_csv(output_dir / "results_phobert" / "per_domain_metrics.csv"), DOMAIN_COLUMNS)
    write_csv(args.output_dir / names[3], read_csv(output_dir / "results" / "learning_curve_summary.csv"), LEARNING_CURVE_COLUMNS)
    write_csv(args.output_dir / names[4], read_csv(output_dir / "results_phobert" / "sequence_length_audit.csv"), SEQUENCE_COLUMNS)
    write_csv(args.output_dir / names[5], confusion_rows(output_dir), ("configuration", "seed", "n", "tn", "fp", "fn", "tp"))

    summary = read_json(output_dir / "results" / "summary.json")
    paired = read_json(output_dir / "results_phobert" / "paired_bootstrap.json")
    split_manifest = read_json(output_dir / "results" / "split_manifest_private.json")
    split_manifest_path = output_dir / "results" / "split_manifest_private.json"
    summary_public = {
        "dataset_commit": split_manifest["dataset_commit"],
        "data_and_split": compact_split_summary(summary),
        "comparison": {k: paired[k] for k in (
            "baseline_configuration", "test_rows", "baseline_macro_f1",
            "phobert_mean_seed_macro_f1", "observed_mean_difference",
            "paired_bootstrap_ci95", "bootstrap_samples", "seeds", "interpretation",
        )},
        "evaluation_scope": "Post-hoc train-derived internal holdout; not independent confirmation.",
    }
    write_json(args.output_dir / names[6], summary_public)
    write_json(args.output_dir / names[7], compact_robustness(output_dir))

    checkpoint = read_json(output_dir / "results_phobert" / "checkpoint_restore_verification.json")
    checkpoint_public = [{k: row[k] for k in (
        "seed", "test_rows", "predictions_identical_to_saved",
        "base_model_revision", "max_length", "micro_batch",
    )} for row in checkpoint]
    write_json(args.output_dir / names[8], checkpoint_public)

    environment = read_json(output_dir / "results_phobert" / "environment.json")
    environment_public = {k: environment[k] for k in (
        "python", "platform", "packages", "cuda_available", "cuda_runtime",
        "gpu", "dataset_commit", "model", "model_revision", "seeds",
    )}
    write_json(args.output_dir / names[9], environment_public)

    artifacts = {name: sha256_file(args.output_dir / name) for name in names[:-1]}
    source_files = expected
    provenance = {
        "artifact_label": "run5_v5",
        "kernel": "hiptetsuya/viocd-phobert-fresh-holdout-run5",
        "kernel_status": "COMPLETE",
        "kernel_last_run_utc": args.kernel_last_run_utc,
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
    write_json(args.output_dir / names[10], provenance)
    print(f"curated_artifacts={len(names)}; raw_rows_published=False; "
          f"functional_code_matches_execution={provenance['source_notebooks']['published_functional_ast_matches_execution']}; "
          f"test_rows={paired['test_rows']}; gpu={environment['gpu']}")


if __name__ == "__main__":
    main()
