# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lưu Xuân Dũng
**Nhóm:** B4 - 2
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Thể hiện hai vector đại diện cho hai đoạn văn bản có hướng gần như trùng nhau trong không gian nhiều chiều, đồng nghĩa với việc hai đoạn văn bản đó có chung chủ đề hoặc ngữ nghĩa rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Quy định đổi trả hàng bị lỗi kỹ thuật trong vòng 48 giờ.
- Câu B: Khách hàng có thể yêu cầu hoàn tiền nếu sản phẩm phát sinh lỗi trong 2 ngày đầu.
- Tại sao tương đồng: Dù dùng từ ngữ khác nhau ("đổi trả" vs "hoàn tiền", "48 giờ" vs "2 ngày") nhưng cả hai đều mang ý nghĩa về chính sách bảo hành khi sản phẩm lỗi.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Quy định đổi trả hàng bị lỗi kỹ thuật.
- Câu B: Hướng dẫn đăng ký tài khoản người bán trên ứng dụng.
- Tại sao khác: Hai câu đề cập đến hai quy trình hoàn toàn không liên quan với nhau (hậu mãi khách hàng vs tạo tài khoản đối tác).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity đánh giá góc giữa hai vector thay vì khoảng cách độ dài tuyệt đối. Điều này giúp loại bỏ ảnh hưởng của độ dài văn bản; hai văn bản có cùng ý nghĩa nhưng một cái dài, một cái ngắn thì góc giữa chúng vẫn nhỏ và cho ra độ tương tự cao.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Kích thước dịch chuyển (step) = 500 - 50 = 450. Số chunk = (10,000 - 50) / 450 = 22.11. Làm tròn lên.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Step giảm xuống còn 400, số chunks tăng lên thành 25. Ta muốn overlap nhiều hơn để tránh việc cắt ngang một câu làm mất đi ngữ cảnh, overlap lớn giúp các chunk giữ được tính liên kết và mạch thông tin liền mạch.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Dùng `re.split` dựa trên các dấu ngắt câu như dấu chấm, chấm than, dấu hỏi chấm hoặc dấu xuống dòng. Sau đó gom nhiều câu lại thành một chunk đến khi đạt max_sentences_per_chunk, đồng thời xử lý loại bỏ các khoảng trắng thừa ở đầu/cuối câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Thuật toán chạy đệ quy với base case là khi độ dài chuỗi `<= chunk_size` hoặc đã hết mảng separators. Văn bản sẽ được chẻ đôi bởi separator hiện tại; nếu một mảnh vẫn quá dài, thuật toán sẽ gọi đệ quy tiếp với separator cấp nhỏ hơn, sau cùng gom lại để không vượt quá kích thước tối đa.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Dữ liệu được lưu trữ dạng dictionary (ID, content, metadata, embedding) vào list (nếu dùng in-memory). Tìm kiếm bằng cách duyệt vòng lặp, tính dot product giữa vector truy vấn và vector của từng bản ghi, sau đó sort giảm dần để lấy top_k điểm cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Lọc (filter) được thực hiện TRƯỚC khi tính điểm để tối ưu hiệu năng tính toán, chỉ tính điểm cho các bản ghi thoả mãn điều kiện metadata. Hàm xóa tạo ra một list comprehension mới, loại bỏ đi các bản ghi có metadata ID hoặc record ID trùng khớp với tham số truyền vào.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Gọi hàm search vào Store để lấy top_k chunks phù hợp, nối các chunks này thành một khối văn bản "Context". Sau đó tiêm khối Context này cùng câu hỏi của user vào System Prompt theo format cố định và đẩy cho LLM xử lý.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\xDg\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: D:\Vin AI\vin-ai\DAY07
plugins: anyio-4.14.2
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
... (Các test khác đều PASS) ...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách trả hàng trong 7 ngày | Khách hàng được hoàn trả sản phẩm trong một tuần | cao | cao | Có |
| 2 | Sản phẩm bị lỗi kỹ thuật do nhà sản xuất | Máy bị hỏng phần cứng từ khi mở hộp | cao | cao | Có |
| 3 | Người bán phải cung cấp hình ảnh chân thực | Thời gian giao hàng dự kiến là 2-3 ngày | thấp | thấp | Có |
| 4 | Thanh toán bằng thẻ tín dụng được miễn phí vận chuyển | Trả tiền bằng thẻ Visa sẽ được freeship | cao | cao | Có |
| 5 | Quý khách vui lòng đánh giá 5 sao sau khi nhận hàng | Hướng dẫn cách khiếu nại lên tổng đài CSKH | thấp | thấp | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Bất ngờ nhất là cặp 4, nơi "thẻ tín dụng" và "thẻ Visa" hay "miễn phí vận chuyển" và "freeship" hoàn toàn khớp nhau dù cấu tạo từ và ngôn ngữ (Việt - Anh) khác biệt. Điều này chứng tỏ embeddings biểu diễn ý nghĩa đa ngôn ngữ (multilingual) rất tốt, nhóm các từ vựng đồng nghĩa vào chung một vùng không gian.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mua điện thoại bị lỗi kỹ thuật thì đổi trả trong bao lâu? | ...đổi trả 1 tháng đầu đối với sản phẩm lỗi kỹ thuật... | 0.89 | Có | Khách hàng được đổi trả trong tháng đầu tiên nếu sản phẩm bị lỗi kỹ thuật... |
| 2 | Thế Giới Di Động thu thập dữ liệu cá nhân của người mua để làm gì? | ...Dữ liệu cá nhân được sử dụng để xác nhận đơn hàng, hỗ trợ sau bán hàng... | 0.91 | Có | Dữ liệu được thu thập nhằm mục đích xác nhận đơn, giao hàng và hỗ trợ hậu mãi. |
| 3 | Có được mang chó mèo vào siêu thị không? | ...Khách hàng không được mang thú cưng (chó, mèo) vào trong khu vực quầy hàng... | 0.85 | Có | Không, siêu thị không cho phép mang thú cưng vào khu vực mua sắm. |
| 4 | Người bán (seller) cần hình ảnh sản phẩm có độ phân giải bao nhiêu? | ...Hình ảnh sản phẩm độ phân giải tối thiểu 1080x1080px, phông nền trắng... | 0.93 | Có | Hình ảnh cần đạt độ phân giải tối thiểu 1080x1080px. |
| 5 | Các phương thức thanh toán khả dụng? | ...Chấp nhận thanh toán qua tiền mặt, thẻ ATM, Visa, trả góp qua thẻ tín dụng... | 0.88 | Có | Bạn có thể thanh toán bằng tiền mặt, thẻ ATM, thẻ tín dụng Visa hoặc mua trả góp. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Mình học được cách điều chỉnh thông số overlap của thuật toán chia đoạn. Nếu tăng overlap lên một chút, các câu trả lời lấy ra không bị đứt gãy ngữ cảnh, đặc biệt với các văn bản có câu văn dài và phức tạp.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
