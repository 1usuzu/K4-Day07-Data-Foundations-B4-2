# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Phương Thùy
**Nhóm:** B4.2
**Ngày:** 03-08-2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có hướng gần nhau, nên hai đoạn văn bản thường có ý
> nghĩa hoặc chủ đề tương tự. Điểm càng gần 1 thì mức tương đồng theo biểu diễn
> của mô hình càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi muốn đổi trả điện thoại bị lỗi.
- Câu B: Làm sao để hoàn tiền cho sản phẩm hỏng?
- Tại sao tương đồng: Cả hai câu cùng nói về hậu mãi khi sản phẩm gặp lỗi,
  đặc biệt là đổi trả hoặc hoàn tiền.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tôi muốn đổi trả điện thoại bị lỗi.
- Câu B: Thời tiết ở Hà Nội hôm nay như thế nào?
- Tại sao khác: Một câu thuộc chủ đề chính sách mua hàng, câu còn lại hỏi về
  thời tiết nên ngữ nghĩa gần như không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine so sánh hướng của các vector, do đó tập trung vào sự giống nhau về
> ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn vector. Khoảng cách Euclid đo độ xa
> tuyệt đối nên có thể thay đổi vì độ lớn embedding, kể cả khi hai văn bản có
> nội dung gần nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11).
>
> Đáp án: 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành ceil((10.000 - 100) / (500 - 100)) = ceil(9.900 / 400)
> = 25 chunks. Overlap lớn hơn giữ được ngữ cảnh ở ranh giới giữa hai chunk,
> nên thông tin hoặc một câu bị cắt ngang ít bị mất khi truy xuất; đổi lại số
> vector, dung lượng lưu trữ và chi phí nhúng tăng lên.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])(?:\s+|$)` để tách sau dấu kết thúc câu, đồng thời
> giữ dấu câu ở cuối mỗi câu. Sau khi tách, các câu được `strip()` rồi gom theo
> `max_sentences_per_chunk`; chuỗi rỗng, khoảng trắng thừa và đoạn cuối không
> có dấu chấm vẫn được xử lý để không làm mất nội dung.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Tôi chọn `RecursiveChunker` cho corpus nhóm vì các chính sách có tiêu đề,
> điều/khoản, đoạn và câu dài không đồng đều. `_split` lần lượt thử `\n\n`,
> `\n`, `. `, khoảng trắng rồi ký tự; nếu một đoạn còn dài hơn `chunk_size`
> thì tiếp tục gọi đệ quy với dấu phân cách tiếp theo. Base case là đoạn đã đủ
> ngắn, không còn separator, hoặc đã đến separator rỗng; khi đó trả về đoạn đó
> thay vì tách tiếp.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được nhúng một lần rồi lưu dưới dạng record gồm `id`, `content`,
> `metadata` và `embedding`; dùng ChromaDB khi sẵn có, nếu không thì dùng list
> trong bộ nhớ với cùng cấu trúc record. Khi tìm kiếm, tôi nhúng query, tính tích
> vô hướng với embedding của từng record (embedding đã chuẩn hóa), sắp xếp điểm
> giảm dần và trả về tối đa `top_k` kết quả kèm score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Tôi lọc metadata trước khi tính điểm để các câu hỏi của người mua chỉ tìm trong
> `customer_role: buyer`, đồng thời có thể phân biệt `category: payment`,
> `returns` và `privacy` trong corpus. `delete_document` xóa mọi record có
> `metadata["doc_id"]` trùng ID cần xóa; cách này xóa đủ các chunk của một tài
> liệu thay vì chỉ xóa một chunk.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` lấy top-k chunk liên quan từ store, đánh số và ghép chúng thành phần
> `Context`, kèm `doc_id` để có thể truy vết tài liệu nguồn. Prompt yêu cầu LLM
> chỉ trả lời dựa trên context, nêu rõ khi context không đủ thông tin, rồi đặt
> câu hỏi ở cuối trước khi gọi `llm_fn`; cách này giúp câu trả lời bám sát các
> chính sách đã thu thập thay vì tự suy đoán.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
pytest tests/ -v
============================== 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Tôi muốn đổi trả điện thoại bị lỗi. | Làm sao để hoàn tiền cho sản phẩm hỏng? | cao | 0,0000 | Không |
| 2 | Tôi muốn đổi trả điện thoại bị lỗi. | Thời tiết ở Hà Nội hôm nay như thế nào? | thấp | 0,0000 | Đúng |
| 3 | Hoàn tiền MoMo mất bao lâu? | Thời hạn nhận tiền hoàn qua ví MoMo là gì? | cao | 0,3873 | Đúng |
| 4 | Thanh toán thẻ ATM cần điều kiện gì? | Khách hàng có thể thanh toán tiền mặt tại siêu thị. | thấp | 0,2132 | Đúng |
| 5 | Dữ liệu cá nhân được sử dụng cho mục đích nào? | Có thể đăng nội dung chiến sự trên mạng xã hội không? | thấp | 0,0769 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 bất ngờ nhất: hai câu cùng chủ đề đổi trả/hoàn tiền nhưng không trùng
> token nên điểm bằng 0. Demo này dùng embedding lexical có chuẩn hóa, vì
> `sentence-transformers` chưa cài được trong môi trường; do đó nó cho thấy
> giới hạn của so khớp từ khóa, không đại diện cho embedding ngữ nghĩa thật.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sạc dự phòng tặng kèm bị hỏng có đổi được không? | Chunk thanh toán thẻ; top-3 có chunk đổi trả liên quan | 0,3166 | Top-1: không; top-3: có | Demo chỉ trích ngữ cảnh, chưa dùng LLM thật |
| 2 | Hoàn tiền cà thẻ mất bao lâu? | Thanh toán thẻ: thời gian hoàn khoảng 7–15 ngày | 0,4636 | Có | Demo trích đúng thời hạn từ context top-1 |
| 3 | Mất hộp khi hoàn tiền có bị thu phí không? | Chính sách đổi trả; top-3 nêu mất phụ kiện/hộp và mức phí | 0,3574 | Top-1: chưa đủ; top-3: có | Demo trích context; cần LLM để tổng hợp câu trả lời |
| 4 | Có được đăng nội dung chiến sự lên trang MXH không? | Chính sách dữ liệu cá nhân (không liên quan) | 0,3566 | Không | Demo không trả lời được do truy xuất sai top-1/top-3 |
| 5 | Dữ liệu cá nhân dùng vào mục đích gì, có bán cho bên thứ ba không? | Chính sách xử lý dữ liệu cá nhân | 0,4359 | Có | Demo trích context về dữ liệu cá nhân; cần LLM để diễn đạt gold answer |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

> Cấu hình demo: `RecursiveChunker(chunk_size=500)`, 178 chunks, embedding
> lexical 512 chiều chuẩn hóa và `EmbeddingStore.search_with_filter()`. Đây là
> demo có thể tái lập khi môi trường chưa tải được model local; cần chạy lại với
> LocalEmbedder hoặc Gemini trước khi dùng làm kết luận cuối cùng của nhóm.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng metadata filter giúp thu hẹp tập ứng viên nhưng không thay
> thế cho embedding ngữ nghĩa: câu hỏi về chiến sự vẫn bị nhiễu bởi từ khóa
> chung. Với corpus chính sách dài, chunk theo tiêu đề/điều khoản và embedder
> đa ngữ thật sẽ quan trọng hơn việc chỉ tăng số lượng chunk.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10 |
| **Tổng phần cá nhân** | **54 / 60** |
