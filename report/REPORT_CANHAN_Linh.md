# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Lê Thị Trúc Linh
**Nhóm:** B4-2
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Nghĩa là hai vector biểu diễn văn bản có hướng (góc) rất gần nhau trong không gian đa chiều, cho thấy nội dung hoặc ngữ nghĩa của chúng rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi rất thích ăn táo."
- Câu B: "Táo là loại trái cây yêu thích của tôi."
- Tại sao tương đồng: Dùng từ ngữ khác nhau nhưng mang cùng một ý nghĩa cốt lõi.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi rất thích ăn táo."
- Câu B: "Hôm nay trời mưa to quá."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn không liên quan đến nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine similarity chỉ quan tâm đến góc (hướng) giữa hai vector chứ không bị ảnh hưởng bởi độ dài (độ lớn) của vector, giúp đánh giá chính xác độ tương đồng ngữ nghĩa bất kể độ dài văn bản gốc là dài hay ngắn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
- Phép tính: Số chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = 22.11 -> 23 chunks
- Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Khi overlap tăng lên 100, số lượng chunk = làm_tròn_lên((10000 - 100) / (500 - 100)) = làm_tròn_lên(9900 / 400) = 24.75 -> 25 chunks (số lượng chunk sẽ tăng lên). Tăng overlap giúp bảo toàn ngữ cảnh tốt hơn khi các câu hoặc ý bị cắt vỡ ở ranh giới giữa các chunk.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Dùng `re.split(r'(\. |\! |\? |\.\n)', text)` để tách câu dựa trên dấu chấm, than, hỏi kèm dấu cách. Xử lý ngoại lệ chuỗi rỗng bằng cách kiểm tra text và `strip()` các khoảng trắng dư thừa, rồi ghép câu với dấu phân cách tương ứng trước khi gộp thành các chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán cố gắng cắt văn bản bằng separator đầu tiên, nếu phần cắt được vẫn lớn hơn `chunk_size` thì gọi đệ quy với danh sách separator còn lại. Base case (cơ sở dừng) là khi chuỗi đã nhỏ hơn `chunk_size` hoặc khi danh sách separator đã cạn (lúc này sẽ ép cắt cứng theo `chunk_size`).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Dữ liệu được lưu trong RAM (in-memory) dưới dạng danh sách các `dict` chứa id, content, metadata và embedding vector. Khi `search`, tính tích vô hướng (dot product) giữa query vector và toàn bộ vector trong store rồi sắp xếp giảm dần theo điểm số để lấy top k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Hàm filter thực hiện lọc *trước* thông qua vòng lặp kiểm tra khớp metadata, sau đó mới gọi search trên tập đã lọc. Chức năng xóa được thực hiện bằng cách khởi tạo lại danh sách `_store` (List comprehension) để chỉ giữ những bản ghi có `id` khác với doc_id bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
Gọi hàm search từ store lấy top k chunk, format gộp chúng lại bằng dấu xuống dòng `\n`. Đưa đoạn này vào prompt theo mẫu "Context:\n{...}\n\nQuestion: {...}\nAnswer:" rồi truyền sang `llm_fn` để lấy câu trả lời cuối cùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.0, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: F:\AI VIN\DAY 07_2\K4-Day07-Data-Foundations-B4-2
collecting ... collected 42 items

...
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.18s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **45 / 60** |
