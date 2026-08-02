# K4 Variant — E-commerce Policy Retrieval

K4 dùng cùng core coding contract với K3, nhưng Phase 2 phải xây dựng knowledge base về **chính sách thương mại điện tử hoặc customer support** (ví dụ: thanh toán, đổi trả, giao hàng, quyền riêng tư, điều kiện người bán).

## Quy tắc riêng của K4

- Mỗi document phải có metadata `customer_role` (ví dụ: `buyer`, `seller`, `both`) và ít nhất một field hữu ích khác.
- Ngoài metadata retrieval, mỗi document phải có `source_url`, `retrieved_at` và `document_version`; chỉ dùng policy công khai hoặc được phép chia sẻ.
- Trong 5 benchmark query, có ít nhất một query cần `metadata_filter={"customer_role": "seller"}` hoặc `buyer`.
- Ít nhất một thành viên thử chunking theo điều/khoản, heading hoặc FAQ pair.
- Gold answer phải trích được từ tài liệu nhóm thu thập; không dùng policy không có trong corpus để chấm retrieval.

Thư mục `data/k4_ecommerce/` có dữ liệu khởi động nhỏ; nhóm vẫn cần bổ sung corpus 5–10 document theo yêu cầu Lab.
