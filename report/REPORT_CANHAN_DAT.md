# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Ngô Lưu Quốc Đạt
**Nhóm:** B4.2
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine giữa 2 văn bản cao tức là góc tạo bởi 2 vector embedding của 2 văn bản đó hẹp => 2 văn bản có tính tương tự cao về mặt ngữ nghĩa.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Tôi rất thích lập trình bằng C#"
- Câu B: "Tôi rất thích viết code bằng ngôn ngữ C#"
- Tại sao tương đồng: Cả hai câu đều nói về việc "lập trình" ~ "viết code", và nói về ngôn ngữ lập trình C#

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tôi thích chơi Valorant vào cuối tuần."
- Câu B: "Phương trình bậc hai có hai nghiệm phân biệt."
- Tại sao khác: Về mặt ngữ nghĩa, hai câu này nói về 2 vấn đề khác nhau, và không có nhiều từ đồng nghĩa

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity bỏ qua độ dài của vector - tức là độ dài của văn bản. Euclid distance bị ảnh hưởng bởi độ dài của văn bản. Trong bài toán so sánh ngữ nghĩa, một văn bản ngắn gọn nhưng đúng ý nghĩa sẽ tốt hơn một văn bản dài nhưng lan man, không bám sát ý nghĩa mong muốn => Ưu tiên Cosine similarity

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Mỗi chunk có 500 ký tự, nhưng sau chunk đầu tiên, mỗi chunk tiếp theo chỉ tiến thêm một đoạn bằng chunk_size - overlap = 500 - 50 = 450 ký tự (vì 50 ký tự cuối của chunk trước được lặp lại ở đầu chunk sau). 
> số chunk = ceil((tổng_độ_dài - chunk_size) / (chunk_size - overlap)) + 1 = 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng từ 23 lên 25 (ceil(9500/400)+1 = 25), vì overlap lớn hơn làm stride mỗi bước nhỏ đi (từ 450 xuống 400 ký tự), nên cần nhiều chunk hơn để phủ hết 10,000 ký tự. Muốn overlap nhiều hơn là để tránh cắt đứt một câu hoặc một ý quan trọng ngay tại ranh giới giữa hai chunk, giúp ngữ cảnh không bị mất khi retrieval trong hệ thống RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])[ \n]+` — điểm mấu chốt là **lookbehind** `(?<=...)`: nó cắt ở khoảng trắng/xuống dòng *sau* dấu kết câu, nên dấu `.` `!` `?` được giữ lại trong câu thay vì bị nuốt mất như khi dùng `split(". ")`. Lớp `[ \n]+` gộp mọi khoảng trắng liên tiếp thành một ranh giới nên không sinh chuỗi rỗng ở giữa các đoạn cách nhau bằng dòng trống.
>
> Ba edge case đã xử lý: (1) text rỗng hoặc chỉ có khoảng trắng → trả `[]` ngay, không trả `[""]`; (2) `.strip()` từng câu rồi lọc bỏ phần tử rỗng, phòng trường hợp văn bản kết thúc bằng dấu chấm khiến `split` sinh phần tử cuối rỗng; (3) `max(1, max_sentences_per_chunk)` trong `__init__` chặn tham số 0 hoặc âm — nếu không, `step = 0` sẽ làm `range()` ném lỗi.
>
> **Hạn chế tôi biết nhưng chưa sửa:** regex coi mọi dấu chấm có khoảng trắng theo sau là kết câu, nên số thứ tự của danh sách đánh số (`1. `, `2. `) bị tách thành "câu" riêng. Trên tài liệu thỏa thuận MXH của nhóm, điều này sinh ra các chunk kết thúc bằng một số lạc lõng như `"…xuất bản phẩm bị cấm. 6."`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Ý tưởng là **thử dấu phân cách theo thứ tự ưu tiên ngữ nghĩa giảm dần** `["\n\n", "\n", ". ", " ", ""]` — ưu tiên cắt ở ranh giới đoạn trước, chỉ khi đoạn vẫn quá dài mới hạ xuống cắt theo dòng, rồi theo câu, rồi theo từ. Nhờ vậy chunk giữ được đơn vị ngữ nghĩa lớn nhất còn vừa `chunk_size`.
>
> **Ba base case** trong `_split`: (1) text rỗng → `[]`; (2) `len(text) <= chunk_size` → trả `[text]`, đây là điều kiện dừng chính của đệ quy; (3) đã hết dấu phân cách hoặc gặp separator `""` → cắt cứng theo `chunk_size` vì không còn cách nào tách theo ngữ nghĩa nữa.
>
> Phần thân dùng chiến lược **gộp tham lam (greedy)**: duyệt các mảnh sau khi `split(separator)` và dồn dần vào `buffer` chừng nào còn vừa `chunk_size` — mục đích là tránh sinh ra hàng loạt chunk vụn khi văn bản có nhiều dòng ngắn. Hai nhánh đệ quy: nếu separator hiện tại không xuất hiện trong text thì bỏ qua, gọi lại với danh sách separator còn lại; nếu một mảnh đơn lẻ vẫn vượt `chunk_size` thì đệ quy riêng mảnh đó với separator ưu tiên thấp hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hoá qua `_make_record()` thành dict gồm `index`, `id`, `content`, `metadata`, `embedding`. Embedding được **tính một lần lúc nạp** rồi lưu kèm record, nên `search` về sau chỉ phải embed đúng câu truy vấn. Trong `metadata` tôi `setdefault("doc_id", doc.id)` để `search_with_filter()` và `delete_document()` luôn có khoá làm việc, kể cả khi tài liệu được tạo không kèm metadata.
>
> Về độ tương tự: `_search_records()` chỉ tính **tích vô hướng** `_dot()` chứ không chia cho tích hai độ dài như công thức cosine đầy đủ. Đây là chủ ý — cả ba embedder trong `src/embeddings.py` đều trả về vector đã chuẩn hoá (`MockEmbedder` chia cho norm, `LocalEmbedder` dùng `normalize_embeddings=True`, OpenAI trả vector đơn vị), mà với vector đơn vị thì `dot(a,b)` **bằng đúng** cosine similarity. Bỏ phép chia thừa giúp giảm chi phí khi phải quét toàn bộ store.
>
> Về lưu trữ: nếu máy có ChromaDB thì tôi ghi song song (mirror) vào collection thật, nhưng **phần xếp hạng luôn chạy trên `self._store`** để điểm số và thứ tự giống hệt nhau dù có hay không có Chroma — nhờ vậy kết quả benchmark tái lập được trên máy bất kỳ thành viên nào. Mọi lỗi từ Chroma đều bị bắt và store tự chuyển hẳn về chế độ bộ nhớ trong thay vì ném exception ra ngoài.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> **Lọc trước, tìm sau (pre-filter).** Tôi lọc `self._store` theo `metadata_filter` để lấy danh sách ứng viên rồi mới chạy similarity trên đó. Nếu làm ngược lại (lấy top-k rồi lọc) thì khi các chunk điểm cao đều không khớp filter, kết quả trả về sẽ ít hơn `top_k` hoặc rỗng — còn pre-filter luôn lấp đủ `top_k` từ đúng nhóm tài liệu cần. Điều kiện khớp dùng `all(...)` nên nhiều khoá trong filter được hiểu là AND.
>
> `delete_document` **dựng lại danh sách** loại bỏ mọi record có `metadata["doc_id"]` trùng, thay vì xoá tại chỗ khi đang duyệt (dễ nhảy sót phần tử). Giá trị trả về xác định bằng cách so sánh độ dài trước/sau — ngắn hơn nghĩa là có xoá, trả `True`; bằng nhau trả `False`. Một tài liệu bị chia thành nhiều chunk nên hàm xoá theo `doc_id` sẽ dọn sạch cả cụm chunk của tài liệu đó trong một lần gọi.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Luồng ba bước theo đúng mẫu RAG: `store.search(question, top_k)` → dựng prompt → gọi `llm_fn`. Nếu store trả về rỗng thì **trả `NO_CONTEXT_MESSAGE` luôn mà không gọi LLM** — vừa tiết kiệm một lần gọi API, vừa chặn nguy cơ mô hình bịa câu trả lời khi không có ngữ cảnh nào.
>
> Ngữ cảnh được đưa vào dưới dạng **các khối có đánh số** `[1]`, `[2]`, `[3]`, mỗi khối kèm `source_url` và điểm tương đồng lấy từ metadata của chunk. Đánh số là để prompt có thể yêu cầu mô hình trích dẫn `[n]` cho từng thông tin, nhờ đó người đọc truy ngược được câu trả lời về đúng chunk và đúng URL gốc — rất cần với dữ liệu chính sách vì người dùng phải kiểm chứng được mức phí, thời hạn.
>
> Prompt đặt ba ràng buộc: chỉ dùng thông tin trong phần NGỮ CẢNH, nói rõ là không biết nếu ngữ cảnh không đủ, và phải trích dẫn số hiệu đoạn. Thứ tự các phần là *chỉ dẫn → NGỮ CẢNH → CÂU HỎI → "TRẢ LỜI:"*, đặt câu hỏi **sau** ngữ cảnh để mô hình đọc câu hỏi ngay trước khi sinh đáp án.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
$ pytest tests/ -v

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED    [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED             [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED      [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED       [  9%]
...
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED     [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED              [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED             [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED        [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED    [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED   [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED         [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED   [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

*(Đã lược bớt phần giữa cho gọn; không có test nào FAILED hay SKIPPED.)*

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Đo bằng `compute_similarity()` trong `src/dat/chunking.py` với embedder `text-embedding-3-small`. Quy ước: ≥ 0,5 là "cao".

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Chính sách đổi trả sản phẩm bị lỗi | Quy định hoàn tiền khi hàng bị hư hỏng | cao | 0,5556 (cao) | ✅ |
| 2 | Tôi muốn trả lại chiếc điện thoại này | Tôi muốn mua một chiếc điện thoại mới | thấp | **0,7151 (cao)** | ❌ |
| 3 | Thời gian bảo hành sản phẩm là bao lâu? | Cửa hàng mở cửa lúc mấy giờ? | thấp | 0,3567 (thấp) | ✅ |
| 4 | Phí đổi trả là 10% giá trị hóa đơn | Mức phí bằng một phần mười tổng số tiền trên hóa đơn | cao | 0,5733 (cao) | ✅ |
| 5 | Chính sách bảo mật dữ liệu cá nhân | Privacy policy for personal data protection | cao | **0,4900 (thấp)** | ❌ |

**Dự đoán đúng: 3/5.**

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> **Cặp 2 gây bất ngờ nhất.** "Tôi muốn *trả lại* điện thoại" và "Tôi muốn *mua* điện thoại mới" là hai ý định **trái ngược nhau** — một bên kết thúc giao dịch, một bên bắt đầu giao dịch — vậy mà đạt 0,7151, **cao nhất trong cả 5 cặp**. Nó thậm chí cao hơn cặp 4 (0,5733) vốn là hai cách diễn đạt của **cùng một sự thật**. Bài học: embedding mã hoá **chủ đề** (topic) chứ không mã hoá **ý định** (intent) hay chiều hướng của hành động. Hai câu chia sẻ cùng miền từ vựng "điện thoại / mua bán / tôi muốn" nên nằm gần nhau trong không gian vector, bất kể chúng nói ngược nhau.
>
> Hệ quả trực tiếp cho hệ thống RAG của nhóm: truy vấn "tôi muốn trả hàng" hoàn toàn có thể kéo về chunk nói chuyện *mua* hàng, và ngược lại. Đây có thể là một phần lý do câu hỏi số 1 của nhóm bị trượt — câu hỏi kể chuyện "tôi mua iPhone hôm thứ 7" khiến các chunk nói về việc *mua/sử dụng sản phẩm* được ưu tiên hơn chunk quy định *đổi phụ kiện đi kèm*. Muốn phân biệt được ý định thì phải bổ sung lọc metadata hoặc bước rerank, chứ chỉ dựa vào cosine similarity là không đủ.
>
> **Cặp 5 cũng đáng chú ý:** cùng nội dung nhưng khác ngôn ngữ Việt–Anh chỉ đạt 0,4900, thấp hơn cả cặp 1 vốn chỉ *liên quan* chứ không đồng nghĩa. Mô hình đa ngữ vẫn giữ một khoảng cách nhất định giữa hai ngôn ngữ, nên corpus tiếng Việt thuần của nhóm là lựa chọn đúng — trộn tài liệu Anh–Việt sẽ làm điểm tương đồng bị lệch.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Cấu hình của tôi: `SentenceChunker(max_sentences_per_chunk=3)`, embedder `text-embedding-3-small`, `top_k=3`, LLM `gpt-4o-mini` (`temperature=0`). Corpus 5 tài liệu → **143 chunk**.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sạc dự phòng tặng kèm iPhone bị hỏng, đổi được không? | `doi-tra-bao-hanh` — "Sản phẩm chỉ dùng cho mục đích cá nhân… Hoàn trả đầy đủ sạc, phụ kiện đi kèm: mất phụ kiện thu phí…" | 0,5168 | ❌ **Không** — chunk gold (mục 1.2 "Phụ kiện đi kèm được đổi miễn phí trong 12 tháng") không có trong top-3 | *"Không biết"* — agent chỉ tìm thấy quy định phụ kiện hãng Hydrus (đổi trong 7 ngày) và tự nhận không đủ thông tin. **Trả lời thiếu nhưng trung thực, không bịa.** |
| 2 | Hoàn tiền cà thẻ bao nhiêu ngày? | `payment-options` — "Hoàn tiền cho giao dịch cà thẻ mất khoảng 7–15 ngày, không tính cuối tuần…" | **0,5741** | ✅ **Có, hạng 1** | *"Khoảng 7–15 ngày, không tính cuối tuần và ngày lễ ([1])"* — **khớp hoàn toàn gold answer**, có trích dẫn nguồn. |
| 3 | Mất hộp sản phẩm khi trả hàng có bị thu phí không? | `doi-tra-bao-hanh` — "Hoàn trả toàn bộ hàng khuyến mãi… Chỉ áp dụng cho sản phẩm chính…" | **0,6176** | ✅ **Có, nhưng ở hạng 3** — chunk chứa "Mất hộp thu phí 2%" nằm hạng 3 chứ không phải hạng 1 | *"Có, bị thu phí 2% giá trị hóa đơn với nhóm Điện thoại, Tablet, Laptop… ([3])"* — **đúng gold answer**, và số `[3]` cho thấy agent dùng đúng chunk hạng 3. |
| 4 | Đăng nội dung chiến sự Israel–Iran lên trang TGDĐ được không? | `thoa-thuan-mxh` — "Nhà cung cấp không chịu trách nhiệm về nội dung website bên ngoài… đảm bảo không vi phạm sở hữu trí tuệ" | 0,5103 | ❌ **Không** — cả 3 chunk đều thuộc đúng tài liệu nhưng không chunk nào chứa Điều 2 (phạm vi nội dung + danh mục cấm) | *"Không biết. Ngữ cảnh không cung cấp thông tin về nội dung chiến sự…"* — **trả lời sai so với gold** (đáng lẽ phải là "Không được"), nhưng agent không bịa. |
| 5 | Thông tin cá nhân dùng vào mục đích gì, có cam kết không bán? | `thoa-thuan-mxh` — "Trường hợp Người sử dụng đăng ký dịch vụ của bên thứ ba… phải tự chịu trách nhiệm bảo mật" | **0,6051** | ✅ **Có, ở hạng 2** — chunk chứa cam kết "không tiết lộ, chia sẻ, cho thuê, hoặc bán" nằm hạng 2 | *"…cam kết không tiết lộ, chia sẻ, cho thuê, hoặc bán thông tin cá nhân… trừ khi khách hàng đồng ý hoặc cơ quan nhà nước yêu cầu ([2])"* — **đúng vế cam kết không bán**, nhưng **thiếu vế mục đích sử dụng** vì chunk mục 2.1 của tài liệu `du-lieu-ca-nhan` không lọt top-3. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **3 / 5** (câu 2, 3, 5)

**Điểm truy xuất theo `docs/SCORING.md`:** câu 2 = 2đ (hạng 1 + trả lời đúng), câu 3 = 1đ (liên quan nhưng không ở hạng 1), câu 5 = 1đ (liên quan hạng 2, trả lời còn thiếu ý), câu 1 và 4 = 0đ → **tổng 4/10**.

**Nhận xét về kết quả của riêng tôi:**
> Hai ca trượt đều rơi vào câu hỏi **dài và nhiều mệnh đề**. Câu 1 kể một tình huống ("mua iPhone thứ 7 tuần trước, sạc dự phòng tặng kèm bị hỏng") nên vector truy vấn bị pha loãng giữa nhiều chủ đề — đúng như hiện tượng tôi quan sát ở cặp 2 mục 4. Câu 4 thì cả 3 chunk đều thuộc đúng tài liệu nhưng lệch điều khoản, cho thấy `SentenceChunker` cắt 3 câu tạo ra chunk quá hẹp so với Điều 2 vốn dài tới 11 khoản liệt kê.
>
> Điểm tôi hài lòng là **agent không bịa ở cả 2 ca trượt** — cả hai đều trả về "Không biết" thay vì suy diễn. Đây là kết quả trực tiếp của ràng buộc "chỉ dùng thông tin trong NGỮ CẢNH, nếu không đủ thì nói rõ là không biết" mà tôi đặt trong `_build_prompt`. Với dữ liệu chính sách, trả lời sai nguy hiểm hơn nhiều so với trả lời "không biết".

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Cấu hình `RecursiveChunker(800)` của Linh đạt 5/10 — cao hơn tôi 1 điểm — với **chỉ 105 chunk so với 143 chunk của tôi**, tức vừa chính xác hơn vừa rẻ hơn. So sánh với `RecursiveChunker(300)` của Dũng (2/10, 293 chunk) cho thấy điều tôi không lường trước: **kích thước chunk ảnh hưởng mạnh hơn thuật toán cắt**. Tôi từng mặc định rằng cắt trọn câu là ưu thế quyết định, nhưng `FixedSizeChunker` của Trang — cắt cứng, hơn 75% ranh giới đứt giữa câu, thậm chí đứt giữa từ — vẫn đạt 4/10 ngang tôi.
>
> Bài học rút ra: điều quan trọng không phải chunk có **đẹp** hay không, mà là chunk có **chứa đủ thông tin để trả lời** hay không. Câu 4 của tôi trượt chính vì lý do đó — chunk 3 câu quá hẹp so với một điều khoản 11 khoản. Nếu làm lại, tôi sẽ tăng `max_sentences_per_chunk` lên 6–8 thay vì thêm overlap (cấu hình overlap của Thùy tốn thêm 46% chunk mà điểm vẫn bằng tôi).

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá | Căn cứ |
|----------|-------------------|--------|
| Khởi động (Warm-up) | 5 / 5 | Hoàn thành cả 1.1 và 1.2; phép tính chunking có trình bày công thức và đã kiểm lại: `ceil((10000−500)/450)+1 = 23`, với overlap 100 thì `ceil(9500/400)+1 = 25`. |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 | Giải thích đủ 5 phần, nêu rõ lý do thiết kế (lookbehind regex, pre-filter, dùng `_dot` vì vector đã chuẩn hoá) và tự chỉ ra hạn chế chưa sửa của `SentenceChunker`. |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 | `pytest tests/ -v` → **42/42 PASSED**, không có FAILED hay SKIPPED. |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 | Đủ 5 cặp có đo số thực tế; dự đoán đúng 3/5 và phần phản ngẫm phân tích được 2 ca sai (topic vs intent, khoảng cách đa ngữ) kèm liên hệ tới lỗi thật của hệ thống. |
| Kết quả truy xuất của tôi (Competition Results) | 4 / 10 | Đo thật: câu 2 = 2đ, câu 3 = 1đ, câu 5 = 1đ, câu 1 và 4 = 0đ. 3/5 câu có chunk liên quan trong top-3. |
| **Tổng phần cá nhân** | **53 / 60** | |
