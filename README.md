# Phát hiện lời phàn nàn trong đánh giá sản phẩm tiếng Việt

Mã nguồn tái lập cho bài tập lớn học phần Xử lý ngôn ngữ tự nhiên: xây dựng và đánh giá hệ thống phân loại đánh giá sản phẩm tiếng Việt thành **có lời phàn nàn (1)** hoặc **không có lời phàn nàn (0)** theo định nghĩa của corpus UIT-ViOCD.

Theo hướng dẫn gốc, nhãn 1 phản ánh sự bất mãn khi thực tế không đạt kỳ vọng; lời khen có thể xuất hiện cùng phàn nàn, và góp ý tích cực vẫn có thể là phàn nàn nếu nêu mong muốn chưa được đáp ứng. Lời lẽ tiêu cực hoặc xúc phạm đơn thuần không tự động mang nhãn phàn nàn. Vì vậy, đây là bài toán phát hiện lời phàn nàn theo định nghĩa corpus, không phải phân loại cảm xúc tích cực/tiêu cực ([bài báo gốc](https://journals.sagepub.com/doi/pdf/10.3233/FAIA210058)).

## Đối tượng sử dụng và tiêu chí nghiệm thu

Đối tượng sử dụng dự kiến là nhân sự chăm sóc khách hàng hoặc kiểm soát chất lượng tại cửa hàng/sàn thương mại điện tử, dùng kết quả phân loại để ưu tiên review cần con người xem xét. Đây là giả định về bối cảnh sử dụng; nhóm chưa khảo sát người dùng và kết quả chưa chứng minh phù hợp triển khai thực tế.

Tiêu chí nghiệm thu của nghiên cứu là: (1) pipeline chạy từ dữ liệu và mô hình đã ghim phiên bản; (2) baseline và PhoBERT được so sánh trên cùng test sau khi lựa chọn cấu hình/epoch bằng validation; (3) Macro-F1 là chỉ số chính, kèm precision, recall và confusion matrix; (4) chỉ kết luận PhoBERT vượt baseline khi cận dưới CI bootstrap ghép cặp 95% lớn hơn 0. Quy tắc diễn giải này được ghi sau các vòng đã xem test, nên không phải tiền đăng ký. Nhóm chưa thống nhất ngưỡng vận hành định lượng với người dùng dự kiến hoặc giảng viên. Kết quả hiện tại mang tính hậu nghiệm; nhóm không tuyên bố hệ thống sẵn sàng triển khai.

## Nội dung kho mã

- `ViOCD_Kaggle_GPU_3seed.ipynb`: notebook tái lập pipeline Run4 trên các split chính thức, từ EDA/tiền xử lý tới demo: ba baseline TF-IDF, PhoBERT ba seed trên GPU, khảo sát quy mô train, robustness và tăng cường bỏ dấu.
- Bản công khai Run4 sửa docstring trong ô mã 3 sau lần chạy Kaggle v10 để mô tả đúng baseline CPU và PhoBERT CUDA. Đây là hiệu chỉnh tài liệu trong docstring, không đổi logic thực thi; provenance tách hash nguồn đã chạy khỏi hash bản công khai và ghi kiểm tra AST sau khi bỏ docstring.
- `ViOCD_Kaggle_Run5_TrainDerivedHoldout_GPU_3seed.ipynb`: notebook Run5 dùng một holdout nội bộ bổ sung được tách từ pool train gốc. Đây là phân tích hậu nghiệm, không phải xác nhận độc lập; các giới hạn được nêu ngay trong notebook và provenance.
- `tools/curate_run5_public_results.py`: tạo các bảng tổng hợp Run5 từ output riêng tư bằng danh sách trường cho phép; không xuất văn bản, mã dòng hoặc dự đoán từng mẫu. CLI từ chối chạy nếu chưa truyền `--confirm-written-rights`, xác nhận bằng văn bản bao gồm cả quyền sử dụng corpus và chia sẻ aggregate; script không thể tự kiểm chứng văn bản đó. Provenance của các aggregate hiện có ghi hash script đúng phiên bản đã tạo chúng. Script hiện tại đã được gia cố kiểm tra chéo/staging sau lần tạo đó; aggregate chưa được tạo lại và sẽ không phát hành thêm khi quyền sử dụng/chia sẻ còn chưa xác nhận.
- Notebook không lưu output cell. Mỗi lần chạy tạo kết quả trong `results/`, `results_phobert/` và `results_robustness/`. `segmented_overlap_audit.json` kiểm tra trùng lặp sau Underthesea giữa các split; `sequence_length_audit.csv` thống kê độ dài PhoBERT và phần mẫu bị cắt ở 128 token; `per_domain_metrics.csv` lưu metric/confusion theo bốn miền.
- `results_public/` chứa các bảng tổng hợp Run4 version 10 và Run5 v5. Các tệp chỉ có thống kê; không có nội dung review, ID dòng, dự đoán từng mẫu, checkpoint, trọng số hay log. Chúng hiện truy cập công khai qua repo này; nhóm chưa có xác nhận bằng văn bản rằng được phép công khai aggregate. Đây là cổng phát hành còn mở, không phải bằng chứng đã được cho phép. Không bổ sung aggregate mới trước khi làm rõ; nếu UIT yêu cầu giới hạn, sẽ hạn chế quyền truy cập hoặc gỡ nội dung liên quan.
- Output đầy đủ của notebook có thêm dự đoán theo từng dòng và các trích đoạn lỗi để phân tích nội bộ; các tệp đó vẫn nằm trong output Kaggle riêng tư. Có 10 ví dụ lỗi baseline và 10 lỗi PhoBERT seed 42, mỗi nhóm gồm 5 dương tính giả và 5 âm tính giả. Sáu ca đối chiếu seed 42 được chọn hậu nghiệm, cân bằng hai ca cho mỗi loại chuyển tiếp; năm ca thuộc miền app, một ca cosmetic, và một ca trùng với danh sách lỗi PhoBERT. Đây là ví dụ minh họa, không đại diện tần suất lỗi. Ghi chú là giả thuyết từ một lượt đọc, chưa được đánh giá độc lập hay xác nhận nguyên nhân; hai ca có thể có ranh giới nhãn hoặc diễn đạt mơ hồ.

Kho mã không phân phối lại corpus hoặc trọng số đã huấn luyện. Notebook tải corpus theo commit cố định từ nguồn, còn PhoBERT được tải theo revision cố định.

## Tái lập trên Kaggle

**Cổng trước tái lập:** trang UIT NLP yêu cầu người dùng ký thỏa thuận; tại 13/11/2026 hồ sơ nhóm chưa lưu xác nhận bằng văn bản. Chỉ tải/xử lý corpus hoặc chạy Run All sau khi quyền sử dụng được xác nhận bằng văn bản. Không công khai aggregate mới trước khi quyền chia sẻ được xác nhận riêng. Các aggregate hiện có vẫn truy cập công khai qua repo này; quyền chia sẻ chúng chưa được xác nhận và đây là cổng phát hành đang mở. Nếu điều kiện của UIT không cho phép giữ chúng, sẽ giới hạn quyền truy cập hoặc gỡ phần bị ảnh hưởng.

1. Tạo Kaggle Notebook mới, giữ notebook ở chế độ **Private**, rồi tải lên `ViOCD_Kaggle_GPU_3seed.ipynb`. Notebook Run5 có thể chạy riêng nếu cần tái tạo phân tích bổ sung; cũng giữ notebook và toàn bộ output ở chế độ riêng tư.
2. Trong Settings, bật Internet và chọn GPU T4. Notebook được chạy thực tế trên Tesla T4; mỗi tiến trình dùng một GPU.
3. **Chỉ sau khi quyền sử dụng corpus đã được xác nhận bằng văn bản**, chạy **Run All**. Cell đầu cài các phiên bản pandas 2.3.3, scikit-learn 1.8.0, Underthesea 9.5.0, matplotlib 3.10.8 và transformers 4.51.3. PyTorch/CUDA được cung cấp bởi môi trường Kaggle. Trước khi cổng quyền mở, dừng ở bước đọc hướng dẫn; không tải/xử lý corpus.
4. Đợi notebook hoàn tất tải dữ liệu và checkpoint. Không cần API token Kaggle hoặc tệp dữ liệu tải lên thủ công.
5. Tải kết quả về nơi lưu trữ nội bộ để kiểm tra. Không công khai văn bản review, ID dòng, dự đoán theo từng mẫu, checkpoint hoặc log riêng tư.

### Phiên bản dữ liệu và mô hình

- Dữ liệu: [UIT-ViOCD trên Hugging Face](https://huggingface.co/datasets/tarudesu/ViOCD), commit `25e1851683ebc407d28e5a2d514b7ae0eadd4e4b`.
- [Bài báo gốc](https://doi.org/10.3233/FAIA210058), [trang UIT NLP](https://sites.google.com/uit.edu.vn/uit-nlp/datasets) và phần mô tả dataset trên Hugging Face ghi 5.485 review; tại lần kiểm tra 13/11/2026, HF Viewer và tổng các split thô của revision ghim đều cho 5.484 (4.387 train + 548 validation + 549 test; xem results_public/data_summary.json). Nhóm báo cáo số dòng thực có, không thêm mẫu; chênh lệch một mẫu về tổng số lượng chưa được giải thích.
- PhoBERT: `vinai/phobert-base`, revision `01daacda68afe13d83023d16ec647239e344a1e6`.
- Hạt giống: 42, 43, 44.
- Chia train/validation/test, quy tắc lọc trùng và chỉ số đánh giá được cố định trong notebook.

## Kết quả thực nghiệm

Trên 546 mẫu được giữ lại sau tiền xử lý từ split test chính thức (549 dòng thô) của Run4, baseline Linear SVM + Underthesea đạt Macro-F1 **91,74%**. PhoBERT đạt trung bình **92,23% ± 0,29 điểm phần trăm SD mẫu** qua ba lượt huấn luyện. CI bootstrap ghép cặp cho chênh lệch là **[−1,72; +2,63] điểm phần trăm**, chứa 0. Run4 đã xem test trong các vòng phát triển trước; kết quả là hậu nghiệm, không xác nhận PhoBERT vượt trội ổn định.

### Run5 — holdout nội bộ train-derived bổ sung

Run5 chọn baseline bằng Macro-F1 validation và chọn epoch PhoBERT bằng validation; baseline C và ba seed PhoBERT được chấm trên cùng 624 mẫu. Baseline C đạt Macro-F1 **89,18%**; PhoBERT đạt **89,88% ± 0,69 điểm phần trăm SD**. Chênh lệch ghép cặp là **+0,70 điểm phần trăm**, CI bootstrap 95% **[−1,79; +3,22] điểm phần trăm**, nên chưa chứng minh mô hình nào vượt trội.

Run5 lấy pool từ 4.157 mẫu train gốc sau làm sạch, rồi chia 3.117/416/624 train/validation/test theo nhãn × miền; loại 75 dòng trùng văn bản với validation/test cũ. Cả ba partition Run5 đều lấy từ pool này, và toàn bộ pool đã được dùng huấn luyện Run4. Cùng split Run5 được dùng qua các phiên bản v1–v5 (v1 chưa hoàn tất; v2–v5 hoàn tất đủ ba seed); một preflight cục bộ cũng làm lộ một phần văn bản cùng chỉ số dòng có thể liên kết tới nhãn công khai. Vì thế Run5 là phân tích hậu nghiệm nội bộ, không phải holdout độc lập ở cấp dự án. Không gộp hai bộ điểm và không dùng chúng để khẳng định PhoBERT tốt hơn.

Các metric Run5, bootstrap, confusion counts, theo miền, learning curve, độ dài token, robustness và provenance tổng hợp nằm trong `results_public/run5_train_holdout_*`. Bảng nguồn cấp từng mẫu vẫn được giữ riêng tư.

Kiểm tra bỏ dấu dùng phép biến đổi mô phỏng trên cùng tập test, không phải đánh giá trên dữ liệu thiếu dấu tự nhiên. Phân tích cặp chẩn đoán gồm 18 cặp do nhóm tự soạn, bao phủ phủ định, khen kèm bất mãn và sai lệch kỳ vọng. Bộ này chưa có cặp riêng cho ngôn ngữ tiêu cực/xúc phạm nhưng không phải lời phàn nàn mang tính xây dựng, nên chỉ mang tính minh họa, chưa bao quát đầy đủ ranh giới nhãn. Các bảng và biểu đồ tổng hợp nằm trong `results_public/`; chúng không chứa dữ liệu từng review. Báo cáo Word thuộc hồ sơ nội bộ, không phát hành trong repo này.


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

Bài báo gốc: Nguyen và cộng sự (2021), *Vietnamese Complaint Detection on E-Commerce Websites*, DOI [10.3233/FAIA210058](https://doi.org/10.3233/FAIA210058). [Dataset card trên Hugging Face](https://huggingface.co/datasets/tarudesu/ViOCD) ghi dữ liệu chỉ dùng cho nghiên cứu và không khai báo giấy phép chuẩn riêng. [Trang UIT NLP Group](https://sites.google.com/uit.edu.vn/uit-nlp/datasets) yêu cầu người dùng UIT-ViOCD liên hệ để ký thỏa thuận corpus. Nhóm chỉ dùng dữ liệu trong BTL, trích dẫn nguồn và không phát hành lại corpus; việc tải được dữ liệu không thay cho thỏa thuận sử dụng. Tính đến 13/11/2026, hồ sơ nhóm chưa lưu văn bản xác nhận. Quyền trình bày/công khai các aggregate trong `results_public/` chưa được xác nhận riêng. Trước khi chạy thêm hoặc phát hành thêm đầu ra dựa trên corpus, cần làm rõ điều kiện với UIT; nếu phản hồi hạn chế các aggregate đang công khai, nhóm sẽ giới hạn quyền truy cập hoặc gỡ phần bị ảnh hưởng.

## Bằng chứng chạy thực tế

Run4 version 10 đã hoàn tất trên Tesla T4 với ba seed, 546 mẫu test được giữ lại sau tiền xử lý ở mỗi seed, dự đoán checkpoint restore trùng hoàn toàn và 77 output files. Demo kiểm tra đầu vào rỗng/không phải chuỗi, hai ví dụ tổng hợp, và review dài 702 token được báo cắt ở giới hạn 128. Run5 v5 đã hoàn tất trên Tesla T4 với ba seed, 624 mẫu, checkpoint restore trùng hoàn toàn và 73 output files; [provenance công khai](results_public/run5_train_holdout_provenance.json) ghi hash nguồn Kaggle, notebook công khai đã làm rõ tài liệu, checksum dữ liệu và các giới hạn phương pháp. Kernel Run4 [riêng tư](https://www.kaggle.com/code/hiptetsuya/viocd-phobert-gpu-3seed-run4) và Run5 [riêng tư](https://www.kaggle.com/code/hiptetsuya/viocd-phobert-fresh-holdout-run5); người chấm cần được chủ tài khoản cấp quyền xem/chạy để kiểm tra log trực tiếp. Mã nguồn và kết quả tổng hợp có thể xem trong repo mà không cần quyền kernel. Repo không chứa corpus, văn bản review, ID dòng, dự đoán từng mẫu, checkpoint, trọng số hay log riêng tư.

## Hướng cải tiến đề xuất

Các hướng dưới đây là đề xuất cho nghiên cứu tiếp theo, chưa nằm trong kết quả đã nghiệm thu:

- Sau khi có quyền sử dụng, thu thập review mới từ thời điểm/nền tảng/nhãn hàng khác; khóa một tập test độc lập trước khi chọn mô hình hoặc ngưỡng và gán nhãn bằng ít nhất hai người độc lập có bước đối chiếu. Không đưa nhãn do mô hình tự sinh vào tập test chuẩn.
- Bổ sung review mới được phép sử dụng cho miền mobile và các trường hợp ranh giới nhãn; test Run4 hiện chỉ có 46 review mobile. Loại trùng với ViOCD và các pool đã dùng; dữ liệu bổ sung chỉ vào train/validation hoặc một test độc lập mới được khóa trước khi tinh chỉnh. Báo cáo metric theo miền kèm khoảng bất định, không suy rộng từ mẫu nhỏ.
- Hiệu chỉnh điểm xác suất và đánh giá cách xử lý review dài hơn giới hạn 128 token. Chọn phương pháp bằng validation hoặc tập phát triển riêng rồi chỉ đánh giá một lần trên test độc lập mới.

## Báo cáo

Báo cáo Word/PDF là hồ sơ nội bộ, không nằm trong repo công khai. Sau khi hoàn tất Word, nhóm cần xuất và kiểm tra PDF trước khi nộp, điền thông tin thành viên trên bìa và cấp quyền Kaggle cho giảng viên.
