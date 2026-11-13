# Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt

Mã nguồn tái lập cho bài tập lớn học phần Xử lý ngôn ngữ tự nhiên: xây dựng và đánh giá hệ thống phân loại đánh giá sản phẩm tiếng Việt thành **có lời phàn nàn (1)** hoặc **không có lời phàn nàn (0)** theo định nghĩa của corpus UIT-ViOCD.

Theo hướng dẫn gốc, nhãn 1 phản ánh sự bất mãn khi thực tế không đạt kỳ vọng; lời khen có thể xuất hiện cùng phàn nàn, và góp ý tích cực vẫn có thể là phàn nàn nếu nêu mong muốn chưa được đáp ứng. Lời lẽ tiêu cực hoặc xúc phạm đơn thuần không tự động mang nhãn phàn nàn. Vì vậy, đây là bài toán phát hiện lời phàn nàn theo định nghĩa corpus, không phải phân loại cảm xúc tích cực/tiêu cực ([bài báo gốc](https://journals.sagepub.com/doi/pdf/10.3233/FAIA210058)).

## Đối tượng sử dụng và tiêu chí nghiệm thu

Đối tượng sử dụng dự kiến là nhân sự chăm sóc khách hàng hoặc kiểm soát chất lượng tại cửa hàng/sàn thương mại điện tử, dùng kết quả phân loại để ưu tiên review cần con người xem xét. Đây là giả định về bối cảnh sử dụng; nhóm chưa khảo sát người dùng và kết quả chưa chứng minh phù hợp triển khai thực tế.

Tiêu chí nghiệm thu của nghiên cứu là: (1) pipeline chạy từ dữ liệu và mô hình đã ghim phiên bản; (2) baseline và PhoBERT được so sánh trên cùng test sau khi lựa chọn cấu hình/epoch bằng validation; (3) Macro-F1 là chỉ số chính, kèm precision, recall và confusion matrix; (4) chỉ kết luận PhoBERT vượt baseline khi cận dưới CI bootstrap ghép cặp 95% lớn hơn 0. Quy tắc diễn giải này được ghi sau các vòng đã xem test, nên không phải tiền đăng ký. Nhóm chưa thống nhất ngưỡng vận hành định lượng với người dùng dự kiến hoặc giảng viên. Kết quả hiện tại mang tính hậu nghiệm; nhóm không tuyên bố hệ thống sẵn sàng triển khai.

## Nội dung kho mã

- `ViOCD_Kaggle_GPU_3seed.ipynb`: notebook tái lập pipeline từ dữ liệu tới demo: EDA/tiền xử lý, ba baseline TF-IDF, PhoBERT ba seed trên GPU, đối chứng đặc trưng, khảo sát quy mô train, robustness, tăng cường bỏ dấu và đánh giá.
- Notebook không lưu output cell. Mỗi lần chạy tạo kết quả trong `results/`, `results_phobert/` và `results_robustness/`. `segmented_overlap_audit.json` kiểm tra trùng lặp sau Underthesea giữa các split; `sequence_length_audit.csv` thống kê độ dài PhoBERT và phần mẫu bị cắt ở 128 token; `per_domain_metrics.csv` lưu metric/confusion theo bốn miền.
- `results_public/` chứa các bảng và biểu đồ tổng hợp đã kiểm tra từ Run4 version 10. Các tệp này không có nội dung review, ID dòng test, dự đoán từng mẫu, checkpoint, trọng số hay log.
- Output đầy đủ của notebook có thêm dự đoán theo từng dòng và các trích đoạn lỗi để phân tích nội bộ; các tệp đó vẫn nằm trong output Kaggle riêng tư. Có 10 ví dụ lỗi baseline và 10 lỗi PhoBERT seed 42, mỗi nhóm gồm 5 dương tính giả và 5 âm tính giả. Sáu ca đối chiếu seed 42 được chọn hậu nghiệm, cân bằng hai ca cho mỗi loại chuyển tiếp; năm ca thuộc miền app, một ca cosmetic, và một ca trùng với danh sách lỗi PhoBERT. Đây là ví dụ minh họa, không đại diện tần suất lỗi. Ghi chú là giả thuyết từ một lượt đọc, chưa được đánh giá độc lập hay xác nhận nguyên nhân; hai ca có thể có ranh giới nhãn hoặc diễn đạt mơ hồ.

Kho mã không phân phối lại corpus hoặc trọng số đã huấn luyện. Notebook tải corpus theo commit cố định từ nguồn, còn PhoBERT được tải theo revision cố định.

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

Kiểm tra bỏ dấu dùng phép biến đổi mô phỏng trên cùng tập test, không phải đánh giá trên dữ liệu thiếu dấu tự nhiên. Phân tích cặp chẩn đoán gồm 18 cặp do nhóm tự soạn, bao phủ phủ định, khen kèm bất mãn và sai lệch kỳ vọng. Bộ này chưa có cặp riêng cho ngôn ngữ tiêu cực/xúc phạm nhưng không phải lời phàn nàn mang tính xây dựng, nên chỉ mang tính minh họa, chưa bao quát đầy đủ ranh giới nhãn. Các bảng và biểu đồ tổng hợp nằm trong `results_public/`; chúng không chứa dữ liệu từng review. Bản Word/PDF của nhóm trình bày đầy đủ diễn giải và giới hạn.


### Tăng cường bỏ dấu và tổng quát hóa theo miền

F0 lặp lại dữ liệu có dấu; F1 ghép dữ liệu gốc với bản bỏ dấu, mỗi điều kiện có 8.314 dòng huấn luyện. Chênh lệch F1 là F1_accent_augmentation trừ F0_clean_duplicate, với bootstrap ghép cặp phân tầng 2.000 lần trên test cố định: test sạch **−0,73 điểm %** (CI95 **[−1,84; +0,37]**); test bỏ dấu mô phỏng **+10,86 điểm %** (CI95 **[+7,75; +14,17]**); sensitivity sau khi loại bốn dòng va chạm sau bỏ dấu (N=542) **+10,95 điểm %** (CI95 **[+7,78; +14,39]**). Khoảng của test sạch chứa 0; kết quả không chứng minh lợi ích trên dữ liệu thiếu dấu tự nhiên.

Đánh giá giữ riêng miền loại toàn bộ ví dụ train thuộc miền được chấm, rồi đo trên các dòng test của miền đó. Macro-F1 của C_word và E_word_char:

| Miền | N test | C_word | E_word_char |
|---|---:|---:|---:|
| app | 194 | 75,81% | 75,52% |
| cosmetic | 149 | 78,81% | 79,93% |
| fashion | 157 | 85,42% | 84,01% |
| mobile | 46 | 89,73% | 89,28% |

Đây là phân tích hậu nghiệm trên test cố định, không phải xác nhận ngoài miền độc lập; kết quả mobile cần thận trọng vì chỉ có 46 mẫu. CSV/JSON cùng manifest tái lập nằm trong `results_robustness/`.

### Khảo sát quy mô tập huấn luyện

Trên validation cố định, cấu hình C đạt Macro-F1 **88,93% ± 1,71 điểm phần trăm SD mẫu** ở 25% train (1.039 mẫu), **90,86% ± 0,99 điểm** ở 50% (2.078), **91,45% ± 0,58 điểm** ở 75% (3.117), và **92,07%** ở 100% (4.157; một lượt, không có SD). Các mức dưới 100% dùng năm lần lấy mẫu phân tầng theo nhãn với seed 42–46. Đây là biến thiên giữa tập con lấy mẫu, không phải biến thiên khởi tạo mô hình.
## Nguồn dữ liệu và giới hạn chia sẻ

Bài báo gốc: Nguyen và cộng sự (2021), *Vietnamese Complaint Detection on E-Commerce Websites*, DOI [10.3233/FAIA210058](https://doi.org/10.3233/FAIA210058). Dataset card trên Hugging Face ghi dữ liệu chỉ dùng cho nghiên cứu và không khai báo giấy phép chuẩn riêng. Nhóm dùng corpus trong phạm vi học thuật của BTL, dẫn nguồn và không phát hành lại dữ liệu. Việc có thể tải dữ liệu không được xem là giấy phép phân phối lại; cần hỏi chủ sở hữu nếu dùng ngoài phạm vi nghiên cứu hoặc muốn phát hành dữ liệu.

## Bằng chứng chạy thực tế

Mỗi kernel Kaggle Run1–Run4 đã có ít nhất một lượt hoàn tất trên GPU Tesla T4. Run4 version 10 là lần chạy hiện hành đã xác minh: `COMPLETE`, ba seed PhoBERT, checkpoint restore trùng dự đoán trên 546 mẫu mỗi seed và 77 output files. Version 10 giữ nguyên pipeline huấn luyện và metric thực nghiệm chính của version 9; chỉ trường `wall_seconds` khác trong bảng seed. Demo đã chạy kiểm tra đầu vào rỗng/không phải chuỗi, hai ví dụ tổng hợp thuộc hai nhãn và review dài 702 token được báo cắt ở giới hạn 128. Demo cache checkpoint seed 42, hiển thị số token được dùng, gọi rõ hai tên nhãn trong bảng softmax và ghi chú điểm chưa hiệu chỉnh. Version 9 đã bổ sung audit chồng lấn sau tách từ, thống kê độ dài/cắt token, chuyển tiếp lỗi ghép cặp, CI theo miền và sáu ca định tính có giới hạn diễn giải. Version 8 là lần chạy xác minh trước đó; version 7 dừng ở cell phân tích do lỗi biến chưa khai báo, không dùng output đó. Version 5 cũng thất bại trước huấn luyện. Các lượt Run3/Run4 v1–v3 được giữ làm lịch sử; không dùng CI tăng cường bỏ dấu sai của chúng. Kernel Run4 [đặt riêng tư](https://www.kaggle.com/code/hiptetsuya/viocd-phobert-gpu-3seed-run4); người chấm cần được chủ tài khoản cấp quyền xem/chạy để kiểm tra log/output trực tiếp. `results_public/` cung cấp các metric tổng hợp để xem mà không cần quyền kernel. Repo không chứa corpus, trích đoạn review, dự đoán từng dòng, checkpoint, trọng số hay log riêng tư.

## Báo cáo

Bản báo cáo Word và PDF có trong gói nộp của nhóm. Trước khi nộp, điền thông tin thành viên trên bìa và cấp quyền Kaggle cho giảng viên.
