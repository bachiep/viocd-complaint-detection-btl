# Graph Report - github_public  (2026-11-13)

## Corpus Check
- 11 files · ~2,468 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: .csv 9, (none) 1, .ipynb 1)

## Summary
- 20 nodes · 17 edges · 5 communities (3 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ddce66dc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt
- Kết quả thực nghiệm
- Tái lập trên Kaggle
- Kết quả tổng hợp công khai
- Q: project scope, dataset, model training, evaluation, artifacts and rubric status

## God Nodes (most connected - your core abstractions)
1. `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` - 8 edges
2. `Q: project scope, dataset, model training, evaluation, artifacts and rubric status` - 4 edges
3. `Kết quả thực nghiệm` - 3 edges
4. `Tái lập trên Kaggle` - 2 edges
5. `Kết quả tổng hợp công khai` - 2 edges
6. `Đối tượng sử dụng và tiêu chí nghiệm thu` - 1 edges
7. `Nội dung kho mã` - 1 edges
8. `Phiên bản dữ liệu và mô hình` - 1 edges
9. `Tăng cường bỏ dấu và tổng quát hóa theo miền` - 1 edges
10. `Khảo sát quy mô tập huấn luyện` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (5 total, 2 thin omitted)

### Community 0 - "Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt"
Cohesion: 0.29
Nodes (6): Báo cáo, Bằng chứng chạy thực tế, Nguồn dữ liệu và giới hạn chia sẻ, Nội dung kho mã, Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt, Đối tượng sử dụng và tiêu chí nghiệm thu

### Community 1 - "Kết quả thực nghiệm"
Cohesion: 0.67
Nodes (3): Khảo sát quy mô tập huấn luyện, Kết quả thực nghiệm, Tăng cường bỏ dấu và tổng quát hóa theo miền

### Community 4 - "Q: project scope, dataset, model training, evaluation, artifacts and rubric status"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: project scope, dataset, model training, evaluation, artifacts and rubric status, Source Nodes

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` connect `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt` to `Kết quả thực nghiệm`, `Tái lập trên Kaggle`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Why does `Kết quả thực nghiệm` connect `Kết quả thực nghiệm` to `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Why does `Tái lập trên Kaggle` connect `Tái lập trên Kaggle` to `Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._