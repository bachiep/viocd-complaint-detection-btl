# Graph Report - github_public  (2026-11-13)

## Corpus Check
- 17 files · ~8,209 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .csv 15, (none) 2, .ipynb 2)

## Summary
- 68 nodes · 123 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5187c1c3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt
- curate_run5_public_results.py
- main
- Kết quả tổng hợp công khai
- Q: project scope, dataset, model training, evaluation, artifacts and rubric status
- source_hash
- validate_run_metadata
- StripDocstrings
- functional_ast_hash
- confusion_rows

## God Nodes (most connected - your core abstractions)
1. `main()` - 21 edges
2. `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` - 9 edges
3. `sha256_bytes()` - 7 edges
4. `StripDocstrings` - 7 edges
5. `notebook_cells()` - 6 edges
6. `functional_ast_hash()` - 6 edges
7. `confusion_rows()` - 6 edges
8. `validate_run_metadata()` - 6 edges
9. `validate_metrics_against_confusion()` - 6 edges
10. `read_json()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `notebook_cells()` --calls--> `read_json()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 2 → community 8_
- `read_json()` --calls--> `json`  [EXTRACTED]
  tools/curate_run5_public_results.py →   _Bridges community 2 → community 5_
- `main()` --calls--> `read_csv()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 9 → community 2_
- `compact_robustness()` --calls--> `require_keys()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 6 → community 2_
- `validate_run_metadata()` --calls--> `require_columns()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 9 → community 6_

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt"
Cohesion: 0.14
Nodes (13): Báo cáo, Bằng chứng chạy thực tế, Hướng cải tiến đề xuất, Khảo sát quy mô tập huấn luyện, Kết quả thực nghiệm, Nguồn dữ liệu và giới hạn chia sẻ, Nội dung kho mã, Phiên bản dữ liệu và mô hình (+5 more)

### Community 1 - "curate_run5_public_results.py"
Cohesion: 0.26
Nodes (4): confusion_metrics(), publish_staged(), require_metric_match(), validate_metrics_against_confusion()

### Community 2 - "main"
Cohesion: 0.40
Nodes (5): compact_robustness(), main(), normalize_utc_timestamp(), paths_overlap(), read_json()

### Community 3 - "Kết quả tổng hợp công khai"
Cohesion: 0.50
Nodes (3): Kết quả Run5 bổ sung, Kết quả tổng hợp công khai, Tệp

### Community 4 - "Q: project scope, dataset, model training, evaluation, artifacts and rubric status"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: project scope, dataset, model training, evaluation, artifacts and rubric status, Source Nodes

### Community 6 - "validate_run_metadata"
Cohesion: 0.67
Nodes (3): compact_split_summary(), require_keys(), validate_run_metadata()

### Community 8 - "functional_ast_hash"
Cohesion: 0.33
Nodes (5): assert_documentation_only(), functional_ast_hash(), notebook_cells(), sha256_bytes(), sha256_file()

### Community 9 - "confusion_rows"
Cohesion: 0.33
Nodes (5): confusion_rows(), read_csv(), require_binary(), require_columns(), write_csv()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StripDocstrings` connect `StripDocstrings` to `functional_ast_hash`, `curate_run5_public_results.py`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Should `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `main` to `curate_run5_public_results.py`, `source_hash`, `validate_run_metadata`, `functional_ast_hash`, `confusion_rows`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._