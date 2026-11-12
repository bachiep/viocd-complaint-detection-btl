# Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt

Mã nguồn tái lập cho bài tập lớn học phần Xử lý ngôn ngữ tự nhiên: xây dựng và đánh giá hệ thống phân loại đánh giá sản phẩm tiếng Việt thành **có lời phàn nàn (1)** hoặc **không có lời phàn nàn (0)** theo định nghĩa của corpus UIT-ViOCD.

## Nội dung kho mã

- `ViOCD_Kaggle_GPU_3seed.ipynb`: notebook chạy từ đầu đến cuối, gồm tiền xử lý, baseline TF-IDF, Linear SVM với Underthesea, tinh chỉnh PhoBERT ba seed trên GPU Kaggle, so sánh ghép cặp, khảo sát quy mô train (25/50/75/100%), phân tích độ bền và thử nghiệm tăng cường dữ liệu.
- Notebook không lưu output cell. Mỗi lần chạy tạo kết quả mới trong thư mục `results/`, `results_phobert/` và `results_robustness/`. `results/error_examples.csv` chứa 5 false positive và 5 false negative kèm trích đoạn ngắn để phân tích trong môi trường chạy; tệp này không được commit vào repo. Khảo sát quy mô lưu `learning_curve_runs.csv`, `learning_curve_summary.csv`, manifest các dòng train và biểu đồ; chỉ dùng validation, test không tham gia.

Kho mã không phân phối lại corpus, các dự đoán mẫu, checkpoint hay trọng số đã huấn luyện. Notebook tải corpus theo commit cố định từ nguồn, còn PhoBERT được tải theo revision cố định.

## Tái lập trên Kaggle

1. Tạo Kaggle Notebook mới và tải lên `ViOCD_Kaggle_GPU_3seed.ipynb`.
2. Trong Settings, bật Internet và chọn GPU T4. Notebook được chạy thực tế trên Tesla T4; mỗi tiến trình dùng một GPU.
3. Chạy **Run All**. Cell đầu cài các phiên bản pandas 2.3.3, scikit-learn 1.8.0, Underthesea 9.5.0, matplotlib 3.10.8 và transformers 4.51.3. PyTorch/CUDA được cung cấp bởi môi trường Kaggle.
4. Đợi notebook hoàn tất tải dữ liệu và checkpoint. Không cần API token Kaggle hoặc tệp dữ liệu tải lên thủ công.
5. Tải các thư mục kết quả trong notebook output để kiểm tra metric, dự đoán và log huấn luyện.

### Phiên bản dữ liệu và mô hình

- Dữ liệu: [UIT-ViOCD trên Hugging Face](https://huggingface.co/datasets/tarudesu/ViOCD), commit `25e1851683ebc407d28e5a2d514b7ae0eadd4e4b`.
- PhoBERT: `vinai/phobert-base`, revision `01daacda68afe13d83023d16ec647239e344a1e6`.
- Hạt giống: 42, 43, 44.
- Chia train/validation/test, quy tắc lọc trùng và chỉ số đánh giá được cố định trong notebook.

## Kết quả thực nghiệm

Trên test 546 mẫu, baseline Linear SVM + Underthesea đạt Macro-F1 **91,74%**. PhoBERT đạt trung bình **92,23% ± 0,29 điểm phần trăm SD mẫu** qua ba lượt huấn luyện. Khoảng bootstrap ghép cặp cho chênh lệch PhoBERT so với baseline chứa 0; thí nghiệm chưa xác nhận PhoBERT vượt trội ổn định.

Kiểm tra bỏ dấu dùng phép biến đổi mô phỏng trên cùng tập test, không phải đánh giá trên dữ liệu thiếu dấu tự nhiên. Phân tích cặp chẩn đoán gồm 18 cặp do nhóm tự soạn và chỉ mang tính thăm dò. Xem báo cáo Word/PDF của nhóm để biết đầy đủ số liệu, khoảng tin cậy, giới hạn và cách diễn giải.


### Khảo sát quy mô tập huấn luyện

Trên validation cố định, cấu hình C đạt Macro-F1 **88,93% ± 1,71 điểm phần trăm SD mẫu** ở 25% train (1.039 mẫu), **90,86% ± 0,99 điểm** ở 50% (2.078), **91,45% ± 0,58 điểm** ở 75% (3.117), và **92,07%** ở 100% (4.157; một lượt, không có SD). Các mức dưới 100% dùng năm lần lấy mẫu phân tầng theo nhãn với seed 42–46. Đây là biến thiên giữa tập con lấy mẫu, không phải biến thiên khởi tạo mô hình.
## Nguồn dữ liệu và giới hạn chia sẻ

Bài báo gốc: Nguyen và cộng sự (2021), *Vietnamese Complaint Detection on E-Commerce Websites*, DOI [10.3233/FAIA210058](https://doi.org/10.3233/FAIA210058). Thẻ dữ liệu Hugging Face nêu mục đích nghiên cứu nhưng không khai báo một giấy phép chuẩn riêng. Nhóm dùng corpus trong phạm vi học thuật, dẫn nguồn và không phát hành lại dữ liệu. Việc sử dụng dữ liệu hoặc trọng số mô hình phải tuân theo điều kiện của chủ sở hữu tương ứng.

## Bằng chứng chạy thực tế

Các lần chạy Kaggle Run1–Run4 đã hoàn tất trên GPU Tesla T4. Run4 bổ sung đầu ra khảo sát quy mô train và mười trích đoạn lỗi sinh trong môi trường chạy. Kernel Run4 [đặt riêng tư](https://www.kaggle.com/code/hiptetsuya/viocd-phobert-gpu-3seed-run4); người chấm cần được chủ tài khoản cấp quyền xem/chạy để kiểm tra log và output. Repo GitHub công khai mã nguồn notebook, không phân phối lại corpus, trích đoạn lỗi, checkpoint hay output riêng tư.

## Báo cáo

Bản báo cáo Word và PDF có trong gói nộp của nhóm. Trước khi nộp, điền thông tin thành viên trên bìa và cấp quyền Kaggle cho giảng viên.