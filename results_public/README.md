# Kết quả tổng hợp công khai

Các tệp không có tiền tố `run5_` là kết quả tổng hợp từ Kaggle Run4 version 10 (`COMPLETE`, Tesla T4). Các tệp `run5_train_holdout_*` được tạo từ snapshot output Kaggle Run5 v5 (`COMPLETE`, Tesla T4). Tham chiếu kernel, dataset, model và hash nguồn có trong các tệp provenance tương ứng.

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

## Kết quả Run5 bổ sung

Run5 chia 4.157 dòng từ pool train gốc thành 3.117/416/624 train/validation/test theo tổ hợp nhãn × miền. Baseline C đạt Macro-F1 89,18%; PhoBERT trung bình 89,88% ± 0,69 điểm phần trăm SD. Chênh lệch ghép cặp là +0,70 điểm phần trăm; CI bootstrap 95% là [−1,79; +3,22] điểm phần trăm và chứa 0.

Đây là holdout nội bộ hậu nghiệm, không phải xác nhận độc lập: toàn bộ pool đã được dùng huấn luyện Run4; cùng split Run5 đã được kiểm tra qua các phiên bản v1–v5 (v1 chưa hoàn tất, còn v2–v5 hoàn tất đủ ba seed); một preflight cục bộ từng hiển thị một phần văn bản cùng chỉ số dòng có thể liên kết tới nhãn công khai. Không gộp kết quả Run5 với Run4. File `run5_train_holdout_provenance.json` lưu giới hạn, hashes nguồn và chỉ ra bản notebook công khai chỉ được làm rõ phần tài liệu; mã tính toán tương đương với mã đã chạy.

`run5_train_holdout_*` được tạo bằng `tools/curate_run5_public_results.py` từ output riêng tư. Script chỉ phát hành các cột tổng hợp allowlist; output theo dòng, văn bản, mã mẫu, checkpoint và log không được sao chép vào repo.

Để tái tạo, tải notebook ở repository, chạy toàn bộ trên Kaggle GPU theo hướng dẫn trong README gốc. Các tệp đầy đủ ở cấp từng mẫu vẫn nằm trong output Kaggle riêng tư, không được phát hành ở đây.
