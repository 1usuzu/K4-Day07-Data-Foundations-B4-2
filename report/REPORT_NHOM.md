# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B4.2
**Thành viên:**
- Lưu Xuân Dũng (MSSV: 2A202601774)
- Ngô Lưu Quốc Đạt (MSSV: 2A202602014)
- Nguyễn Phương Thùy (MSSV: 2A202601953)
- Nguyễn Thị Huyền Trang (MSSV: 2A202601960)
- Lê Thị Trúc Linh (MSSV: 2A202601322)
**Ngày:** 03-08-2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K4):** Chính sách thương mại điện tử / hỗ trợ khách hàng (thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán…).

**Phạm vi cụ thể nhóm tập trung:**
> Các chính sách công khai dành cho khách hàng của một nhà bán lẻ duy nhất (Thế Giới Di Động — thegioididong.com): đổi trả/hoàn tiền, thanh toán, xử lý dữ liệu cá nhân, nội quy cửa hàng và thỏa thuận sử dụng mạng xã hội.

Chọn **một nhà bán lẻ duy nhất** thay vì gom nhiều sàn để các tài liệu dùng chung một hệ thuật ngữ và không mâu thuẫn nhau về mức phí/thời hạn — nhờ đó gold answer luôn truy được về đúng một nguồn.

### Danh sách tài liệu (Data Inventory)

Tất cả tài liệu lưu tại `data/k4_ecommerce/`, kiểm kê trong `data/k4_ecommerce/sources.csv`.

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Thỏa thuận sử dụng trang mạng xã hội<br>`k4-tgdd-thoa-thuan-mxh` | https://www.thegioididong.com/thoa-thuan-su-dung-trang-mxh | 2026-08-03 / `not-stated` | 26.757 | `customer_role: both`, `category: social-terms`, `language: vi`, `region: vn` |
| 2 | Chính sách xử lý dữ liệu cá nhân<br>`k4-tgdd-du-lieu-ca-nhan` | https://www.thegioididong.com/chinh-sach-xu-ly-du-lieu-ca-nhan | 2026-08-03 / `2026-01-01` | 11.976 | `customer_role: both`, `category: privacy`, `language: vi`, `region: vn` |
| 3 | Chính sách đổi trả<br>`k4-tgdd-doi-tra-bao-hanh` | https://www.thegioididong.com/chinh-sach-bao-hanh-san-pham | 2026-08-03 / `2024-10-11` | 7.716 | `customer_role: buyer`, `category: returns`, `language: vi`, `region: vn` |
| 4 | Nội quy cửa hàng<br>`k4-tgdd-noi-quy-cua-hang` | https://www.thegioididong.com/noi-quy-cua-hang | 2026-08-03 / `2014-06-01` | 3.955 | `customer_role: both`, `category: store-rules`, `language: vi`, `region: vn` |
| 5 | Quy định thanh toán<br>`k4-payment-options` | https://www.thegioididong.com/thanh-toan | 2026-08-03 / `not-stated` | 1.451 | `customer_role: buyer`, `category: payment`, `language: vi` |

Số ký tự đếm trên phần nội dung đã làm sạch (không tính YAML front matter).

**Quy trình thu thập:** dùng `scripts/fetch_public_pages.py` — kiểm tra `robots.txt` trước mỗi URL, khai báo `User-Agent` của lab, chờ 5 giây giữa các request theo đúng `Crawl-delay: 5` mà site công bố. Sau khi tải, mỗi trang được **làm sạch thủ công**: bỏ menu điều hướng, hộp chọn Tỉnh/Phường, popup xin đồng ý dữ liệu, banner và footer lặp lại; giữ nguyên toàn bộ mức phí, thời hạn, điều kiện và ngoại lệ. Không thêm bất kỳ thông tin nào không có trong nguồn.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
  - Cả 5 URL đều là trang chính sách công khai, không cần đăng nhập, và được `robots.txt` của thegioididong.com cho phép (đã kiểm tra từng URL bằng `robots_allowed()`).
  - Thông tin liên hệ còn giữ lại (`cskh@thegioididong.com`, hotline 1800.1062 / 1900 232 464) là kênh liên hệ doanh nghiệp công bố công khai, không phải dữ liệu cá nhân.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
  - `document_version` lấy trực tiếp từ trang nguồn khi có nêu ("Ngày cập nhật: 11.10.2024"; "Cập nhật và áp dụng từ ngày 01/01/2026"; "Số 01.06-2014/KD.TGDD"). Hai trang không công bố ngày ban hành nên ghi `not-stated` thay vì suy đoán.
  - Đã đối chiếu `sources.csv` khớp 1-1 với file `.md` trên đĩa, và `source_url` + `document_version` trong CSV khớp front matter.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `k4-tgdd-doi-tra-bao-hanh` | Định danh ổn định, không dấu; dùng để truy vết chunk về đúng tài liệu gốc khi chấm gold answer. |
| `customer_role` | enum: `buyer` / `seller` / `both` | `buyer` | **Trường bắt buộc của K4.** Lọc theo vai trò người hỏi: câu hỏi của người mua không nên trả về điều khoản chỉ ràng buộc nhà cung cấp. |
| `category` | enum | `returns`, `payment`, `privacy`, `store-rules`, `social-terms` | Khoanh vùng chủ đề khi truy vấn mơ hồ. Cần thiết vì corpus có 2 tài liệu cùng nói về dữ liệu cá nhân (`privacy` và `social-terms`) — lọc `category` tách được chúng. |
| `document_version` | date-string \| `not-stated` | `2024-10-11` | Phân biệt phiên bản chính sách khi cùng một quy định có nhiều mốc hiệu lực; giúp phát hiện nội dung đã lỗi thời (`2014-06-01`). |
| `source_url` | URL | `https://www.thegioididong.com/thanh-toan` | Trích dẫn nguồn kèm câu trả lời để người dùng tự kiểm chứng. |
| `retrieved_at` | date `YYYY-MM-DD` | `2026-08-03` | Cho biết dữ liệu cũ tới mức nào so với trang gốc hiện tại. |
| `language` | ISO code | `vi` | Chuẩn bị cho corpus đa ngữ; hiện toàn bộ là `vi`. |
| `region` | string | `vn` | Lọc theo phạm vi áp dụng địa lý của chính sách. Hiện có ở 4/5 tài liệu (thiếu ở `k4-payment-options`). |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| payment-options.md | FixedSizeChunker (`fixed_size`) | 7 | 286 ký tự | Cắt khá cứng, đôi lúc cắt đôi câu khiến ngữ cảnh bị đứt đoạn. |
| payment-options.md | SentenceChunker (`by_sentences`) | 5 | 338 ký tự | Giữ ngữ cảnh tốt nhất vì cắt theo đúng dấu chấm câu. |
| payment-options.md | RecursiveChunker (`recursive`) | 9 | 187 ký tự | Chunk chia nhỏ hơn, bám theo đoạn/heading, thích hợp tra cứu chi tiết. |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Lưu Xuân Dũng]**
- **Loại chiến lược:** RecursiveChunker (chunk_size=300)
- **Mô tả & lý do chọn cho chủ đề này:** Chọn Recursive vì văn bản chính sách thương mại thường phân cấp theo Heading và các gạch đầu dòng rõ ràng. Việc đệ quy chia theo đoạn và câu giúp bóc tách từng điều khoản tách bạch mà không bị gãy ngữ cảnh.
- **Code snippet (nếu custom):**
```python
# Sử dụng logic mặc định trong src/dung/chunking.py 
# overlap = 50, max_sentences_per_chunk = 5
```

**Thành viên 2 — [Ngô Lưu Quốc Đạt]**
- **Loại chiến lược:** SentenceChunker (`max_sentences_per_chunk=3`, không overlap)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản chính sách thương mại được viết theo câu khá chuẩn — mỗi câu thường gói trọn một điều kiện đầy đủ (mức phí, thời hạn, ngoại lệ). Cắt đúng ranh giới câu nên giữ nguyên được cặp *điều kiện → hệ qu, tránh tình trạng `FixedSizeChunker` cắt ngang giữa mệnh đề làm mất con số hoặc mất vế điều kiện. Cấu trúc câu và đoạn văn của nguồn cũng đều đặn nên ranh giới câu là tín hiệu phân đoạn đáng tin cậy hơn cắt theo số ký tự cố định.
- **Kết quả đo trên corpus thật:** `doi-tra-bao-hanh` 24 chunk (TB 320 ký tự) · `thoa-thuan-mxh` 65 chunk (TB 410 ký tự) · `payment-options` 5 chunk (TB 288 ký tự). Kích thước chunk biến thiên theo độ dài câu thật thay vì bị ép về một con số cố định như `fixed_size`.
- **Hạn chế đã phát hiện:** regex nhận diện câu cắt sau mọi `.` `!` `?` có khoảng trắng/xuống dòng theo sau, nên số thứ tự của danh sách đánh số bị hiểu nhầm là kết câu. Trên `thoa-thuan-mxh` (văn bản nhiều danh sách đánh số) sinh ra các chunk kết thúc bằng một số lạc lõng, ví dụ `"…xuất bản phẩm bị cấm. 6."` — số `6.` của mục kế tiếp bị kéo vào cuối chunk hiện tại, làm lệch nhóm 3 câu. Hướng khắc phục: thêm điều kiện loại trừ khi ký tự trước dấu chấm chỉ là chữ số.
- **Code snippet (nếu custom):**
```python
# src/dat/chunking.py — SentenceChunker
# Cắt SAU dấu kết câu (lookbehind) để giữ lại dấu chấm/hỏi/than trong câu.
_BOUNDARY = re.compile(r"(?<=[.!?])[ \n]+")

sentences = [part.strip() for part in self._BOUNDARY.split(text)]
sentences = [sentence for sentence in sentences if sentence]   # bỏ chuỗi rỗng
step = self.max_sentences_per_chunk                            # mặc định 3
return [
    " ".join(sentences[start : start + step]).strip()
    for start in range(0, len(sentences), step)
]
```

**Thành viên 3 — [Nguyễn Phương Thùy]**
- **Loại chiến lược:** SentenceChunker **có overlap** (`max_sentences_per_chunk=3`, `overlap_sentences=1` → bước nhảy 2 câu)
- **Mô tả & lý do chọn cho chủ đề này:** Giữ nguyên ưu điểm cắt theo ranh giới câu của Thành viên 2, nhưng thêm chồng lấn 1 câu giữa hai chunk liền kề để xử lý điểm yếu lớn nhất của bản không overlap: trong văn bản chính sách, điều kiện và ngoại lệ thường nằm ở câu kế tiếp câu quy định mức phí. Ví dụ mục 1.2 nêu "Tháng đầu tiên kể từ ngày mua miễn phí…" rồi câu sau mới là "Lưu ý: Nếu không có sản phẩm chính đổi cho Khách hàng thì áp dụng…". Nếu ranh giới chunk rơi đúng giữa hai câu này, chunk truy xuất được sẽ mất vế ngoại lệ và agent trả lời thiếu. Overlap 1 câu đảm bảo mỗi câu xuất hiện ở hai chunk liên tiếp, nên dù ranh giới rơi vào đâu thì vẫn còn một chunk chứa trọn cặp "quy định + ngoại lệ".
- **Đánh đổi:** overlap làm tăng số chunk và dung lượng lưu trữ/embedding. Đo trên corpus: `doi-tra-bao-hanh` 24 → **35 chunk** (tổng ký tự lưu 1,39×), `thoa-thuan-mxh` 65 → **97 chunk** (1,47×), `payment-options` 5 → **6 chunk** (1,36×). Đổi lại khoảng 40–50% chi phí embedding để giảm rủi ro mất ngữ cảnh ở ranh giới — với corpus nhỏ (5 tài liệu) thì chi phí này chấp nhận được.
- **Code snippet (nếu custom):**
```python
# src/thuy/chunking.py — SentenceChunker thêm tham số overlap_sentences
def __init__(self, max_sentences_per_chunk: int = 3, overlap_sentences: int = 1) -> None:
    self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)
    # overlap phải nhỏ hơn kích thước cửa sổ, nếu không vòng lặp sẽ không tiến
    self.overlap_sentences = min(max(0, overlap_sentences), self.max_sentences_per_chunk - 1)

def chunk(self, text: str) -> list[str]:
    if not text or not text.strip():
        return []
    sentences = [p.strip() for p in self._BOUNDARY.split(text)]
    sentences = [s for s in sentences if s]

    step = self.max_sentences_per_chunk - self.overlap_sentences   # 3 - 1 = 2
    chunks = []
    for start in range(0, len(sentences), step):
        window = sentences[start : start + self.max_sentences_per_chunk]
        if window:
            chunks.append(" ".join(window).strip())
        if start + self.max_sentences_per_chunk >= len(sentences):
            break        # cửa sổ đã chạm cuối, dừng để không sinh chunk lặp
    return chunks
```

**Thành viên 4 — [Nguyễn Thị Huyền Trang]**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=500`, `overlap=50` — mặc định trong `src/trang/chunking.py`)
- **Mô tả & lý do chọn cho chủ đề này:** Đây là chiến lược đơn giản và dễ dự đoán nhất: mọi chunk đều có kích thước gần bằng nhau nên chi phí embedding và độ trễ truy vấn ổn định, không phụ thuộc cách hành văn của từng tài liệu. Corpus của nhóm có độ dài rất chênh lệch (từ 1.451 đến 26.757 ký tự) nhưng `fixed_size` vẫn cho chunk đều nhau, tiện làm **mốc đối chứng (baseline)** để đo xem hai chiến lược cắt theo ngữ nghĩa của Thành viên 2 và 3 thực sự tốt hơn bao nhiêu. Overlap 50 ký tự bù đắp một phần cho việc cắt cứng ở ranh giới.
- **Kết quả đo trên corpus thật:** `doi-tra-bao-hanh` 18 chunk (TB 476 ký tự) · `thoa-thuan-mxh` 60 chunk (TB 495 ký tự) · `payment-options` 4 chunk (TB 400 ký tự). Số chunk **ít nhất** trong ba chiến lược, độ dài trung bình bám sát `chunk_size` — đúng như kỳ vọng.
- **Hạn chế đã phát hiện:** cắt theo số ký tự nên ranh giới rơi tùy ý vào giữa câu, thậm chí **giữa từ**. Đo tỷ lệ chunk bắt đầu từ giữa một câu: `doi-tra-bao-hanh` 10/17, `thoa-thuan-mxh` 46/59, `payment-options` 2/3 — tức **hơn 75% ranh giới cắt ngang câu**. Ví dụ thực tế trong `doi-tra-bao-hanh`: một chunk mở đầu bằng `"àn hình máy tính, Máy tính bảng…"` (đứt giữa từ "Màn"), một chunk khác bắt đầu bằng `"o hành quá 15 ngày hoặc phải bảo hành lại sản phẩm…"` — vế điều kiện bị tách khỏi vế hệ quả "được áp dụng Hư gì đổi nấy hoặc Hoàn tiền với mức phí giảm 50%". Overlap 50 ký tự quá ngắn so với câu chính sách trung bình (~100–150 ký tự) nên không cứu được các trường hợp này.
- **Code snippet (nếu custom):**
```python
# src/trang/chunking.py — dùng logic mặc định, không tùy biến
step = self.chunk_size - self.overlap          # 500 - 50 = 450
for start in range(0, len(text), step):
    chunks.append(text[start : start + self.chunk_size])
    if start + self.chunk_size >= len(text):
        break                                  # đã lấy hết phần đuôi
```

**Thành viên 5 — [Lê Thị Trúc Linh]**
- **Loại chiến lược:** RecursiveChunker (`chunk_size=800`, separators mặc định `["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng chung chunker với Thành viên 1 nhưng **cửa sổ lớn hơn gấp gần 3 lần (800 so với 300)**, tạo thành một **so sánh có kiểm soát**: giữ nguyên thuật toán, chỉ đổi kích thước, để đo riêng ảnh hưởng của `chunk_size` tách khỏi ảnh hưởng của chiến lược. Lý do chọn cửa sổ lớn: trong chính sách đổi trả, phần **"Điều kiện áp dụng" nằm tách bên dưới** khối quy định mức phí (mục 1.2 và 1.3 đều theo cấu trúc *quy định → danh sách điều kiện*). Cửa sổ 300 ký tự thường không đủ chứa cả cụm, khiến chunk trả về chỉ có mức phí mà thiếu điều kiện đi kèm; cửa sổ 800 giữ trọn được cả cụm điều khoản trong một chunk.
- **Kết quả đo trên corpus thật:** `doi-tra-bao-hanh` 15 chunk (TB 514 ký tự) · `thoa-thuan-mxh` 59 chunk (TB 454 ký tự) · `payment-options` 3 chunk (TB 484 ký tự).
- **So sánh trực tiếp với `chunk_size=300` của Thành viên 1** (cùng `RecursiveChunker`, cùng tài liệu):

  | chunk_size | thoa-thuan-mxh | Chunk vụn (<40 ký tự) | doi-tra-bao-hanh |
  |---|---|---|---|
  | 300 | 157 chunk, TB 170 | **27** | 44 chunk, TB 175 |
  | 800 | 59 chunk, TB 454 | **4** | 15 chunk, TB 514 |

  Cửa sổ 300 sinh ra 27 mảnh vụn dưới 40 ký tự trên `thoa-thuan-mxh` — phần lớn là các dòng tiêu đề `### Điều …` và số thứ tự danh sách bị tách riêng thành chunk độc lập. Những mảnh này gần như vô dụng khi truy xuất vì không mang nội dung quy định, nhưng vẫn chiếm chỗ trong vector store và có thể lọt vào top-k. Cửa sổ 800 giảm còn 4 mảnh.
- **Đánh đổi:** chunk lớn làm embedding "loãng" hơn — một vector phải đại diện cho nhiều ý, nên với câu hỏi rất hẹp (ví dụ "hoàn tiền cà thẻ mấy ngày?") điểm tương đồng có thể thấp hơn so với chunk nhỏ đúng trọng tâm. Đây chính là giả thuyết nhóm sẽ kiểm chứng bằng 5 câu hỏi đánh giá.
- **Code snippet (nếu custom):**
```python
# src/linh/chunking.py — dùng logic đệ quy mặc định, chỉ đổi chunk_size
chunker = RecursiveChunker(chunk_size=800)   # thay vì 500 mặc định / 300 của TV1
# _split() thử lần lượt "\n\n" → "\n" → ". " → " " → ""
# và chỉ xuống mức tách nhỏ hơn khi đoạn hiện tại vẫn vượt chunk_size
```

### So Sánh Giữa Các Thành Viên

Chạy 5 câu hỏi đánh giá của nhóm trên cùng corpus, cùng embedder `text-embedding-3-small` (OpenAI), `top_k=3`, chỉ khác chiến lược chia chunk. Điểm dưới đây **chỉ chấm phần truy xuất**: 2đ nếu chunk chứa gold answer ở hạng 1, 1đ nếu nằm hạng 2–3, 0đ nếu không có trong top-3.

| Thành viên | Chiến lược (Strategy) | Số chunk | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|---------|----------------------|-----------|----------|
| Lê Thị Trúc Linh | RecursiveChunker (800) | 105 | **5** | Cao điểm nhất. Chunk lớn giữ trọn cụm *quy định + điều kiện áp dụng*, nên là chiến lược duy nhất lấy được chunk Điều 2 của thỏa thuận MXH ở câu 4. Ít chunk nhất (105) → rẻ nhất khi embedding. | Chunk lớn làm vector "loãng", câu 5 (hỏi 2 ý ở 2 tài liệu) không lọt top-3. |
| Ngô Lưu Quốc Đạt | SentenceChunker (3 câu) | 143 | 4 | Chunk luôn trọn câu nên đọc ra là hiểu, không cần ghép mảnh. Câu 5 đạt hạng 2 — tốt nhất nhóm ở câu này. | Câu 3 chỉ đạt hạng 3. Ranh giới 3 câu cắt rời cụm *quy định ↔ điều kiện*. |
| Nguyễn Phương Thùy | SentenceChunker (3 câu, overlap 1) | 209 | 4 | Overlap giúp câu 5 vẫn vào top-3 dù hỏi 2 ý. Bao phủ ranh giới tốt hơn bản không overlap. | Tăng 46% số chunk so với TV2 nhưng **không tăng điểm** — chi phí embedding cao hơn mà hiệu quả ngang bằng. |
| Nguyễn Thị Huyền Trang | FixedSizeChunker (500, overlap 50) | 118 | 4 | Bất ngờ ngang điểm hai chiến lược ngữ nghĩa. Câu 3 đạt hạng 1 nhờ chunk 500 ký tự chứa trọn danh sách phí. | Hơn 75% ranh giới cắt ngang câu, có chỗ đứt giữa từ. Câu 4 và 5 đều trượt top-3. |
| Lưu Xuân Dũng | RecursiveChunker (300) | 293 | 2 | Chunk nhỏ, đúng trọng tâm khi câu hỏi rất hẹp (câu 2 đạt hạng 1). | **Thấp nhất.** 293 chunk, trong đó nhiều mảnh vụn <40 ký tự (tiêu đề, số thứ tự) chiếm chỗ trong top-3 và đẩy chunk có nội dung ra ngoài. 4/5 câu trượt. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker với `chunk_size` lớn (800) là tốt nhất cho chủ đề chính sách TMĐT** — 5/10 điểm, đồng thời rẻ nhất khi embedding (105 chunk, chỉ bằng 1/3 của cấu hình 300). Nhưng kết luận quan trọng hơn con số xếp hạng là: **kích thước chunk quyết định nhiều hơn thuật toán cắt**. Bằng chứng là cặp đối chứng có kiểm soát Dũng–Linh: cùng `RecursiveChunker`, cùng separators, chỉ đổi 300 → 800 mà điểm nhảy từ 2 lên 5; trong khi ba chiến lược *khác thuật toán* nhưng có chunk cỡ trung bình tương đương (Sentence 320–410 ký tự, Fixed 500) lại dồn cụm ở đúng 4 điểm.
>
> Lý do nằm ở cấu trúc của văn bản chính sách: các điều khoản luôn viết theo dạng **quy định → danh sách "Điều kiện áp dụng" tách bên dưới** (mục 1.2, 1.3 của chính sách đổi trả). Cửa sổ hẹp cắt rời hai vế này nên chunk truy được chỉ có mức phí mà mất điều kiện; cửa sổ 300 còn sinh 27 mảnh vụn dưới 40 ký tự (tiêu đề `### Điều …`, số thứ tự) chen vào top-3 và đẩy chunk có nội dung ra ngoài. Chunk lớn giữ trọn cụm điều khoản nên thắng ở câu 4 — câu duy nhất cần cả phạm vi cho phép lẫn danh mục nội dung cấm.
>
> **Hai kết quả đi ngược trực giác, đáng chú ý nhất:** (a) overlap **không đáng tiền** ở corpus này — cấu hình của Thùy tốn thêm 46% chunk so với Đạt mà điểm y hệt (4/10), vì overlap chỉ cứu được ranh giới giữa 2 câu liền kề, trong khi lỗi thật lại là cụm *quy định + điều kiện* cách nhau tới 5–7 câu; (b) `FixedSizeChunker` — chiến lược "ngây thơ" nhất — vẫn ngang điểm hai chiến lược cắt theo ngữ nghĩa, cho thấy với embedding đủ tốt thì việc chunk có trọn câu hay không ít quan trọng hơn việc chunk có **chứa đủ thông tin** để trả lời hay không.
>
> *Giới hạn của kết luận:* chỉ 5 câu hỏi nên chênh lệch 1 điểm nằm trong sai số — khi chạy lại, cấu hình của Thùy dao động giữa 4 và 5 do hai chunk ở hạng 3–4 chênh nhau chưa tới 0,001 điểm tương đồng. Khoảng cách đáng tin duy nhất là 5 so với 2 (Linh so với Dũng). Ngoài ra điểm này chỉ đo phần truy xuất, chưa chấm độ chính xác câu trả lời của agent.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Tôi mua điện thoại iPhone vào hôm thứ 7 tuần trước. Sạc dự phòng tặng kèm bị hỏng. Tôi có thể đổi sạc dự phòng khác không?<br><br>*(Câu cần lọc metadata: `customer_role: buyer`)* | **Được, nếu sạc dự phòng là phụ kiện đi kèm máy.** Theo mục 1.2, phụ kiện đi kèm được đổi **miễn phí trong vòng 12 tháng** kể từ ngày mua sản phẩm chính, đổi bằng phụ kiện cùng công năng mà TGDĐ/ĐMX đang kinh doanh, chất lượng tương đương. Mua "thứ 7 tuần trước" nên vẫn còn trong 12 tháng → không mất phí. Nếu không có phụ kiện tương đương hoặc khách không thích thì áp dụng bảo hành hãng.<br><br>**Ngoại lệ phải nêu:** nếu sạc dự phòng được tính là **hàng khuyến mãi**, mục 2 quy định không áp dụng bảo hành/đổi trả tại TGDĐ mà phải liên hệ bảo hành hãng. | `k4-tgdd-doi-tra-bao-hanh` → mục **1.2** (gạch đầu dòng "Hư phụ kiện đi kèm…")<br>Chunk đối chứng: mục **2** (nhóm phụ kiện không điện, sản phẩm khuyến mãi) |
| 2 | Nếu tôi muốn hoàn tiền cà thẻ thì bao nhiêu ngày sau nhận được? | **Khoảng 7–15 ngày.** Với giao dịch cà thẻ tại siêu thị/khi nhận hàng: hoàn tiền mất **khoảng 7–15 ngày, không tính cuối tuần và ngày lễ**. Nếu thanh toán trực tuyến bằng thẻ thì tiền hoàn về đúng phương thức đã dùng, thời gian dự kiến **7–15 ngày làm việc** với Visa/MasterCard/JCB (ATM qua OnePay 7–10 ngày). Quá thời hạn có thể liên hệ TGDĐ để được hỗ trợ. | `k4-payment-options` → mục **Thanh toán bằng thẻ**<br>Chunk bổ sung: mục **Hoàn tiền khi đã thanh toán trực tuyến** |
| 3 | Khi trả hàng hoàn tiền mà tôi làm mất hộp sản phẩm thì có bị thu phí không? | **Vẫn trả được nhưng bị thu phí.** Điều kiện hoàn tiền yêu cầu hoàn trả đầy đủ hộp, sạc, phụ kiện đi kèm; **mất hộp thu 2% giá trị hóa đơn** với nhóm Điện thoại, Tablet, Laptop, Màn hình máy tính, Máy tính để bàn, Đồng hồ, Máy in. Mất phụ kiện thu theo giá tối thiểu trên website TGDĐ/ĐMX hoặc chính hãng, **tối đa 5% giá trị hóa đơn** (riêng Camera tối đa 100% giá trị sản phẩm). Khoản này cộng thêm vào phí hoàn tiền: tháng đầu 20% giá trị hóa đơn, tháng 2–12 là 10%/tháng. | `k4-tgdd-doi-tra-bao-hanh` → mục **1.3** (Hoàn tiền + Điều kiện áp dụng, gạch đầu dòng "Hoàn trả lại đầy đủ hộp, sạc, phụ kiện đi kèm") |
| 4 | Tôi có thể đăng tải nội dung chiến sự Israel và Iran lên trang của Thegioididong không? | **Không được.** Hai căn cứ độc lập tại Điều 2: (a) phạm vi nội dung được phép chỉ giới hạn ở **thông tin công nghệ, khoa học kỹ thuật phục vụ hoặc liên quan đến sản phẩm, dịch vụ của Thế Giới Di Động** — tin chiến sự nằm ngoài phạm vi này; (b) khoản 1 cấm nội dung **tuyên truyền chiến tranh, khủng bố; gây hận thù, mâu thuẫn giữa các dân tộc, sắc tộc, tôn giáo**. Ngoài ra bài viết phải qua Bộ phận kiểm duyệt nội dung mới được đăng; vi phạm bị xử lý theo Điều 5 (nhắc nhở 1 lần, tái phạm thì khóa quyền đăng bài hoặc xóa tài khoản vĩnh viễn). | `k4-tgdd-thoa-thuan-mxh` → **Điều 2** (đoạn mở đầu + khoản 1)<br>Chunk bổ sung: **Điều 5** (quy trình xử lý vi phạm) |
| 5 | Thông tin cá nhân của khách hàng khi đăng ký tài khoản và mua hàng sẽ được sử dụng cho những mục đích gì, và có được cam kết không bán cho bên thứ ba không?<br><br>*(Câu cần lọc metadata: `category`, vì 2 tài liệu cùng nói về dữ liệu cá nhân)* | **Mục đích sử dụng** (mục 2.1): đăng ký/xác thực tài khoản; xác nhận đơn hàng, trạng thái giao hàng, hủy đơn, xử lý thanh toán, giao–lắp đặt, bảo hành, đối soát, **hoàn tiền, đổi trả**, xử lý khiếu nại, hậu mãi; chăm sóc và hỗ trợ khách hàng; nghĩa vụ pháp luật (xuất hóa đơn, cung cấp cho cơ quan nhà nước); phòng chống gian lận. Mục 2.2 nêu nhóm mục đích ngoài thỏa thuận (quảng cáo, khuyến mại) — **khách hàng có quyền đồng ý hoặc không cho từng mục đích**.<br><br>**Cam kết không bán:** có. Nhà cung cấp **không tiết lộ, chia sẻ, cho thuê, hoặc bán** thông tin cá nhân/thông tin riêng cho tổ chức, cá nhân khác với bất kỳ mục đích nào, **trừ khi** người dùng đồng ý hoặc cơ quan nhà nước có thẩm quyền yêu cầu.<br><br>**Lưu ý:** mục 4 vẫn cho phép *chuyển giao* dữ liệu cho đối tác giao hàng, viễn thông, bảo hiểm, công ty liên kết, luật sư/kiểm toán, bên xử lý dữ liệu theo hợp đồng — chia sẻ để thực hiện dịch vụ khác với bán dữ liệu. | `k4-tgdd-du-lieu-ca-nhan` → mục **2.1**, **2.2** (mục đích) và mục **4** (chuyển giao)<br>`k4-tgdd-thoa-thuan-mxh` → **Điều 8** khoản 4 (cam kết không bán) |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Đổi trả đt lỗi... | SentenceChunker (overlap) | Có (Top 1) | Lấy đủ ý sạc dự phòng + hàng khuyến mãi. Điểm: 2 |
| 2 | Hoàn tiền cà thẻ... | FixedSizeChunker | Có (Top 1) | Văn bản ngắn, cắt kiểu gì cũng trúng. Điểm: 2 |
| 3 | Mất hộp thu phí... | RecursiveChunker (300) | Có (Top 2) | Lấy được mức thu phí 2% nhưng thiếu ý tối đa 5%. Điểm: 1 |
| 4 | Đăng nội dung chiến sự... | SentenceChunker (overlap) | Có (Top 1) | Bắt được chuẩn xác Điều 2 (cấm tuyên truyền chiến tranh). Điểm: 2 |
| 5 | Dữ liệu cá nhân... | RecursiveChunker (800) | Có (Top 1) | Chunk lớn giúp gom đủ cả mục đích và cam kết chia sẻ. Điểm: 2 |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, vô cùng hữu ích ở **Câu 1** và **Câu 5**. Ở câu 1, lọc `customer_role: buyer` giúp loại bỏ các chính sách đổi trả dành cho đối tác. Ở câu 5, lọc `category: privacy` giúp Agent tập trung vào "Chính sách xử lý dữ liệu cá nhân" thay vì bị nhiễu bởi các quy định bảo mật bên "Thỏa thuận mạng xã hội".

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
- Sự chênh lệch độ dài của corpus (có file >26.000 ký tự, có file <1.500 ký tự) đòi hỏi chiến lược chia đoạn linh hoạt, không thể dùng 1 size cố định.
- Đối với văn bản pháp lý/chính sách, ranh giới ngữ nghĩa (dấu chấm câu, ngắt đoạn) quan trọng hơn số lượng ký tự. Cắt giữa câu sẽ làm hỏng kết quả của LLM.

**Bài học rút ra khi so sánh trong nhóm:**
- Cùng một bộ tài liệu, nhưng chiến lược thêm **Overlap** giúp LLM trả lời "người lớn" và chặt chẽ hơn hẳn so với việc không có overlap, dù tốn thêm không gian lưu trữ. Kích thước chunk lớn (800) đôi khi bị loãng ngữ nghĩa so với chunk nhỏ (300) nếu câu hỏi quá hẹp.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
- Nhóm sẽ tiến hành làm sạch dữ liệu (Data Cleaning) kỹ hơn: loại bỏ các số thứ tự lửng lơ ở đầu dòng để tránh làm rối regex của SentenceChunker. Đồng thời, chia các file quá lớn thành nhiều file nhỏ theo từng Chương để gắn Metadata chuẩn xác hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
