# Kết quả tổng hợp công khai

Các tệp trong thư mục này được trích từ output Kaggle Run4 version 9 (`COMPLETE`, Tesla T4). Tham chiếu đầy đủ về kernel, dataset, model và hash source có trong `provenance.json`.

Đây là bảng/biểu đồ tổng hợp để người đọc xem kết quả mà không cần quyền truy cập kernel riêng tư. Thư mục không chứa corpus, văn bản đánh giá, ID dòng test, dự đoán từng dòng, checkpoint, trọng số hay log chạy. Các khoảng tin cậy và phép thử dùng cùng tập test cố định đã được xem ở những vòng trước; chúng là phân tích hậu nghiệm, không phải xác nhận độc lập. Không diễn giải kết quả bỏ dấu mô phỏng như dữ liệu thiếu dấu tự nhiên.

## Tệp

- `baseline_metrics.csv`, `phobert_seed_metrics.csv`, `model_comparison.csv`: metric baseline, từng seed và tổng hợp.
- `paired_bootstrap.json`, `per_domain_paired_bootstrap.csv`: chênh lệch ghép cặp và khoảng bootstrap.
- `per_domain_metrics.csv`, `error_counts_by_domain.csv`, `paired_error_transition_summary.csv`: phân tích lỗi tổng hợp theo miền, nhãn và seed.
- `learning_curve_summary.csv`: khảo sát quy mô train trên validation.
- `data_summary.json`, `sequence_length_audit.csv`: thống kê split, audit trùng sau tách từ và độ dài token.
- `robustness_summary.json`, `accent_augmentation.json`, `accent_augmentation_uncertainty_summary.json`: phân tích độ bền và tăng cường bỏ dấu; trường chứa ID mẫu đã bị loại khỏi bản công khai.
- `environment.json`, `checkpoint_restore_verification.json`, `provenance.json`: môi trường và truy vết phiên bản.
- `evaluation.png`, `learning_curve.png`: biểu đồ tổng hợp.

Để tái tạo, tải notebook ở repository, chạy toàn bộ trên Kaggle GPU theo hướng dẫn trong README gốc. Các tệp đầy đủ ở cấp từng mẫu vẫn nằm trong output Kaggle riêng tư, không được phát hành ở đây.
