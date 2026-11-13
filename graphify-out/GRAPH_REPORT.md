# Graph Report - github_public  (2026-11-13)

## Corpus Check
- 17 files · ~5,529 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 18 file(s) not represented in the graph (top: .csv 15, .ipynb 2, (none) 1)

## Summary
- 51 nodes · 82 edges · 10 communities (7 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `846947b4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt
- Kết quả thực nghiệm
- Tái lập trên Kaggle
- Kết quả tổng hợp công khai
- Q: project scope, dataset, model training, evaluation, artifacts and rubric status
- curate_run5_public_results.py
- main
- StripDocstrings
- functional_ast_hash
- confusion_rows

## God Nodes (most connected - your core abstractions)
1. `main()` - 14 edges
2. `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` - 8 edges
3. `StripDocstrings` - 7 edges
4. `sha256_bytes()` - 6 edges
5. `notebook_cells()` - 6 edges
6. `functional_ast_hash()` - 6 edges
7. `read_json()` - 5 edges
8. `source_hash()` - 5 edges
9. `read_csv()` - 4 edges
10. `assert_documentation_only()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `read_csv()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 9 → community 6_
- `assert_documentation_only()` --calls--> `sha256_bytes()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 8 → community 6_
- `functional_ast_hash()` --calls--> `StripDocstrings`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 7 → community 8_
- `main()` --calls--> `compact_split_summary()`  [EXTRACTED]
  tools/curate_run5_public_results.py → tools/curate_run5_public_results.py  _Bridges community 5 → community 6_

## Import Cycles
- None detected.

## Communities (10 total, 3 thin omitted)

### Community 0 - "Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt"
Cohesion: 0.29
Nodes (6): Báo cáo, Bằng chứng chạy thực tế, Nguồn dữ liệu và giới hạn chia sẻ, Nội dung kho mã, Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt, Đối tượng sử dụng và tiêu chí nghiệm thu

### Community 1 - "Kết quả thực nghiệm"
Cohesion: 0.50
Nodes (4): Khảo sát quy mô tập huấn luyện, Kết quả thực nghiệm, Run5 — holdout nội bộ train-derived bổ sung, Tăng cường bỏ dấu và tổng quát hóa theo miền

### Community 3 - "Kết quả tổng hợp công khai"
Cohesion: 0.50
Nodes (3): Kết quả Run5 bổ sung, Kết quả tổng hợp công khai, Tệp

### Community 4 - "Q: project scope, dataset, model training, evaluation, artifacts and rubric status"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: project scope, dataset, model training, evaluation, artifacts and rubric status, Source Nodes

### Community 6 - "main"
Cohesion: 0.46
Nodes (7): assert_documentation_only(), compact_robustness(), main(), notebook_cells(), read_json(), source_hash(), write_json()

### Community 8 - "functional_ast_hash"
Cohesion: 0.40
Nodes (3): functional_ast_hash(), sha256_bytes(), sha256_file()

### Community 9 - "confusion_rows"
Cohesion: 0.40
Nodes (3): confusion_rows(), read_csv(), write_csv()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StripDocstrings` connect `StripDocstrings` to `functional_ast_hash`, `curate_run5_public_results.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` connect `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` to `Kết quả thực nghiệm`, `Tái lập trên Kaggle`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `main()` connect `main` to `functional_ast_hash`, `confusion_rows`, `curate_run5_public_results.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._