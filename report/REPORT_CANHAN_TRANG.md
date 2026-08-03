# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trang
**Nhóm:** K4-B4-2
**Ngày:** 03/08/2026

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là góc giữa hai vector biểu diễn từ (embeddings) trong không gian nhiều chiều rất nhỏ. Điều này chỉ ra hai đoạn văn bản có độ tương đồng ngữ nghĩa rất lớn, mặc dù chúng có thể sử dụng các từ vựng khác nhau hoặc có độ dài khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Làm thế nào để tôi đổi trả hàng?"
- Câu B: "Tôi muốn hoàn lại sản phẩm này thì phải làm sao?"
- Tại sao tương đồng: Cả hai câu đều thể hiện chung một ý định/nhu cầu của người dùng là muốn hoàn trả lại sản phẩm đã mua, chỉ là cách diễn đạt từ ngữ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Chính sách đổi trả hàng trực tuyến."
- Câu B: "Mặt trời luôn mọc ở hướng Đông."
- Tại sao khác: Hai câu này thuộc hai lĩnh vực ngữ cảnh hoàn toàn khác biệt nhau (chính sách TMĐT vs hiện tượng thiên văn), không có mối liên quan nào về nghĩa.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Bởi vì khoảng cách Euclid bị ảnh hưởng bởi độ dài (độ lớn) của các vector, điều này có nghĩa là các văn bản dài hơn (chứa nhiều từ lặp lại) sẽ bị kéo giãn ra xa nhau mặc dù chúng có cùng nội dung nghĩa. Ngược lại, độ tương tự cosine chỉ quan tâm đến hướng của vector (góc giữa chúng), giúp loại bỏ sự ảnh hưởng của độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Số lượng chunk = làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11) = 23
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi tăng overlap lên 100, số lượng chunk mới là: làm_tròn_lên((10000 - 100) / (500 - 100)) = làm_tròn_lên(9900 / 400) = làm_tròn_lên(24.75) = 25 chunks (tăng thêm 2 chunks).
> Ta muốn độ chồng chéo nhiều hơn để giữ trọn vẹn ngữ cảnh giữa các ranh giới chunk, ngăn việc thông tin quan trọng nằm giữa hai chunk bị cắt đứt làm giảm khả năng hiểu nghĩa của mô hình RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng regex lookbehind `re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)` để tách văn bản thành các câu mà không làm mất dấu câu cuối câu. Sau đó, tiến hành làm sạch câu rỗng, gom các câu vào các nhóm có kích thước tối đa là `max_sentences_per_chunk` rồi nối lại bằng dấu cách `" "` để tạo ra các chunk hoàn chỉnh.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Giải thuật hoạt động bằng đệ quy chia nhỏ. Trường hợp cơ sở (base case) là khi văn bản nhỏ hơn `chunk_size` hoặc không còn dấu phân tách nào khả dụng (chia theo ký tự). Với mỗi bước đệ quy, ta lấy dấu phân tách đầu tiên khả dụng để `split` văn bản thành các đoạn nhỏ. Các đoạn con nào vượt quá `chunk_size` sẽ được tiếp tục gọi đệ quy với dấu phân tách tiếp theo, sau đó ta gộp các đoạn nhỏ lại sao cho độ dài của chunk gộp không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Hỗ trợ cả hai chế độ: in-memory (sử dụng list để lưu trữ các dictionary bản ghi) và ChromaDB. Khi thực hiện `search`, đối với in-memory ta tính tích vô hướng (dot product) giữa vector truy vấn và toàn bộ vector trong cơ sở dữ liệu bằng hàm `_dot`, sau đó sắp xếp giảm dần theo điểm số để chọn ra Top-K.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Thực hiện kỹ thuật lọc trước (pre-filtering). Với in-memory, ta duyệt qua tất cả bản ghi và chỉ giữ lại những bản ghi khớp toàn bộ các trường trong `metadata_filter` trước khi thực hiện tìm kiếm tương tự. Hàm `delete_document` sẽ loại bỏ các phần tử trong danh sách bằng cách so sánh cả `id` (nếu add tài liệu trực tiếp) và `metadata["doc_id"]` (nếu nạp qua pipeline chunking).

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi phương thức `search` từ vector store để tìm ra Top-K chunk có độ tương tự cao nhất. Sau đó, gộp nội dung các chunk này lại bằng dấu xuống dòng kép `\n\n` làm ngữ cảnh (context). Dựng prompt RAG hoàn chỉnh đưa vào `llm_fn` để mô hình tạo ra câu trả lời cuối cùng dựa trên dữ liệu.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: D:\HT\AI_Vinuni\Lab7\K4-Day07-Data-Foundations-B4-2
plugins: anyio-4.14.2
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.15s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Làm thế nào để đổi trả hàng?" | "Tôi muốn hoàn lại sản phẩm này." | cao | 0.1502 | Đúng |
| 2 | "Quy định giao hàng nhanh là gì?" | "Sản phẩm giao trong bao lâu?" | cao | -0.2387 | Sai |
| 3 | "Mặt trời mọc ở hướng Đông." | "Tôi muốn mua sắm trực tuyến." | thấp | 0.2382 | Sai |
| 4 | "Làm thế nào để đổi trả hàng?" | "Hôm nay trời nắng đẹp." | thấp | -0.0598 | Đúng |
| 5 | "Chính sách bán hàng dành cho đối tác." | "Quy định đăng bán dành cho người bán." | cao | -0.1094 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là cặp câu 3 ("Mặt trời mọc ở hướng Đông" vs "Tôi muốn mua sắm trực tuyến") lại có điểm tương tự cao hơn rất nhiều so với cặp câu 2 và 5 (vốn có sự tương đồng mạnh về ý nghĩa). Điều này xảy ra do `MockEmbedder` chỉ là hàm băm MD5 ngẫu nhiên và không hiểu ngữ nghĩa. Nó chứng minh rằng embeddings thực tế cần được huấn luyện sâu (Deep Learning) trên kho dữ liệu khổng lồ mới có thể ánh xạ được cấu trúc ý nghĩa của ngôn ngữ thay vì tính toán toán học ngẫu nhiên.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

*(Thực hiện test với Mock Embedder trên tập dữ liệu mặc định data/k4_ecommerce)*

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời hạn người mua gửi yêu cầu đổi trả là bao lâu? | `seller-listing.md` (Đăng bán sản phẩm...) | 0.2716 | Không | [Demo Response using context...] |
| 2 | Người bán có trách nhiệm gì khi đăng bán sản phẩm? | `returns-policy.md` (Đổi trả hàng...) | 0.1269 | Không | [Demo Response using context...] |
| 3 | Người mua cần chuẩn bị gì khi yêu cầu đổi trả hàng bị lỗi? | `returns-policy.md` (Đổi trả hàng...) | 0.0709 | Có | [Demo Response using context...] |
| 4 | Sản phẩm nào không được phép đăng bán trên sàn? | `seller-listing.md` (Đăng bán sản phẩm...) | 0.1874 | Có | [Demo Response using context...] |
| 5 | Quy trình phản hồi yêu cầu đổi trả của người bán như thế nào? | `returns-policy.md` (Đổi trả hàng...) | 0.1595 | Có | [Demo Response using context...] |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi nhận thấy rằng việc chia nhỏ văn bản (chunking) theo ranh giới câu hoặc tiêu đề thực tế giúp tăng khả năng tìm kiếm chính xác hơn nhiều so với việc chỉ chia theo kích thước cố định, vì nó bảo toàn trọn vẹn được một ý hoàn chỉnh. Ngoài ra, việc thiết kế metadata lọc hợp lý (như `customer_role`) đóng vai trò quan trọng trong việc thu hẹp phạm vi tìm kiếm của Agent.

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
