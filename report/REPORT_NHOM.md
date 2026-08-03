# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** B4.2
**Thành viên:** Lưu Xuân Dũng, Ngô Lưu Quốc Đạt, Nguyễn Phương Thùy, Nguyễn Thị Huyền Trang, Lê Thị Trúc Linh
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
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

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
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
