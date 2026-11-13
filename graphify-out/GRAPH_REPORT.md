# Graph Report - github_public  (2026-11-13)

## Corpus Check
- 17 files · ~8,995 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .csv 15, (none) 2, .ipynb 2)

## Summary
- 69 nodes · 126 edges · 8 communities (7 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c51821b7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt
- curate_run5_public_results.py
- main
- Kết quả tổng hợp công khai
- Q: project scope, dataset, model training, evaluation, artifacts and rubric status
- StripDocstrings
- functional_ast_hash
- confusion_rows

## God Nodes (most connected - your core abstractions)
1. `main()` - 22 edges
2. `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` - 9 edges
3. `sha256_bytes()` - 8 edges
4. `StripDocstrings` - 7 edges
5. `notebook_cells()` - 6 edges
6. `functional_ast_hash()` - 6 edges
7. `confusion_rows()` - 6 edges
8. `validate_run_metadata()` - 6 edges
9. `validate_metrics_against_confusion()` - 6 edges
10. `read_json()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `read_csv()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 9 → community 2_
- `main()` --calls--> `publish_staged()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 1 → community 2_
- `assert_reviewed_publication_changes()` --calls--> `sha256_bytes()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 8 → community 2_
- `validate_run_metadata()` --calls--> `sha256_bytes()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 8 → community 9_
- `functional_ast_hash()` --calls--> `StripDocstrings`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 7 → community 8_

## Import Cycles
- None detected.

## Communities (8 total, 1 thin omitted)

### Community 0 - "Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt"
Cohesion: 0.14
Nodes (13): Báo cáo, Bằng chứng chạy thực tế, Hướng cải tiến đề xuất, Khảo sát quy mô tập huấn luyện, Kết quả thực nghiệm, Nguồn dữ liệu và giới hạn chia sẻ, Nội dung kho mã, Phiên bản dữ liệu và mô hình (+5 more)

### Community 1 - "curate_run5_public_results.py"
Cohesion: 0.26
Nodes (4): confusion_metrics(), publish_staged(), require_metric_match(), validate_metrics_against_confusion()

### Community 2 - "main"
Cohesion: 0.24
Nodes (11): assert_reviewed_publication_changes(), compact_robustness(), compact_split_summary(), main(), normalize_utc_timestamp(), notebook_cells(), paths_overlap(), read_json() (+3 more)

### Community 3 - "Kết quả tổng hợp công khai"
Cohesion: 0.50
Nodes (3): Kết quả Run5 bổ sung, Kết quả tổng hợp công khai, Tệp

### Community 4 - "Q: project scope, dataset, model training, evaluation, artifacts and rubric status"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: project scope, dataset, model training, evaluation, artifacts and rubric status, Source Nodes

### Community 8 - "functional_ast_hash"
Cohesion: 0.33
Nodes (4): functional_ast_hash(), sha256_bytes(), sha256_file(), sha256_normalized_text_file()

### Community 9 - "confusion_rows"
Cohesion: 0.29
Nodes (6): confusion_rows(), read_csv(), require_binary(), require_columns(), validate_run_metadata(), write_csv()

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StripDocstrings` connect `StripDocstrings` to `functional_ast_hash`, `curate_run5_public_results.py`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Should `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` be split into smaller, more focused modules?**
  _Cohesion score 0.14285714285714285 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `main` to `functional_ast_hash`, `curate_run5_public_results.py`, `confusion_rows`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._