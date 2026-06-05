# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hoàng Dương
**MSSV** 2A20260849
**Nhóm:** C5
**Ngày:** 05/06/2024

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai đoạn văn bản có độ tương đồng cao về ngữ nghĩa và hướng của vector biểu diễn, dù độ dài văn bản có thể khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: "Học máy là một lĩnh vực của trí tuệ nhân tạo."
- Sentence B: "Trí tuệ nhân tạo bao gồm các kỹ thuật học máy."
- Tại sao tương đồng: Cả hai câu đều nói về mối quan hệ giữa học máy và AI.

**Ví dụ LOW similarity:**
- Sentence A: "Hôm nay trời nắng đẹp."
- Sentence B: "Mô hình ngôn ngữ lớn cần nhiều dữ liệu."
- Tại sao khác: Nội dung hoàn toàn khác biệt, một bên nói về thời tiết, một bên nói về kỹ thuật AI.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì cosine similarity tập trung vào hướng của vector (ngữ nghĩa) thay vì độ dài (số lượng từ), giúp xử lý tốt các đoạn văn bản có độ dài khác nhau nhưng cùng nội dung.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> num_chunks = ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.11)
> Đáp án: 23

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Số lượng chunk sẽ tăng lên vì bước nhảy (step) giảm xuống. Muốn overlap nhiều hơn để đảm bảo ngữ cảnh ở biên các chunk không bị mất, giúp AI hiểu được mối liên hệ giữa các đoạn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Tuyển sinh Công an nhân dân (CAND) năm 2026

**Tại sao nhóm chọn domain này?**
> Đây là lĩnh vực có quy định khắt khe, nhiều con số (chỉ tiêu, mã ngành) và điều kiện chi tiết. Việc sử dụng RAG sẽ giúp thí sinh tra cứu nhanh chóng và chính xác các quy định thay vì phải đọc file PDF dài.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | thongbaotuyensinh.md | Bộ Công an | ~18,800 | type: main_notice |
| 2 | phu-luc-01-chi-tieu-dai-hoc-2026.md | Bộ Công an | ~4,600 | type: quota |
| 3 | phu-luc-02-to-hop-mon-ma-bai-thi.md | Bộ Công an | ~1,800 | type: exam_code |
| 4 | phu-luc-03-chi-tieu-vb2ca-2026.md | Bộ Công an | ~2,100 | type: quota_vb2 |
| 5 | rag_system_design.md | Nhóm tự biên soạn | ~2,400 | type: technical_note |
| 6 | vector_store_notes.md | Nhóm tự biên soạn | ~2,100 | type: technical_note |
| 7 | customer_support_playbook.txt | Giả lập | ~1,700 | type: playbook |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| type | string | main_notice, quota, technical_note | Phân loại mục đích văn bản để ưu tiên tìm kiếm trong các nguồn tin chính thống hoặc phụ trợ. |
| category | string | dai_hoc, trung_cap, vb2 | Lọc chính xác thông tin theo hệ đào tạo mà thí sinh quan tâm, tránh nhiễu từ các hệ khác. |
| region | string | phia_bac, phia_nam | Rất quan trọng trong CAND vì chỉ tiêu và địa điểm thi thường phân biệt rõ rệt theo khu vực địa lý. |
| year | integer | 2026 | Đảm bảo Agent luôn truy xuất thông tin mới nhất, tránh nhầm lẫn với các quy định cũ của các năm trước. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| thongbaotuyensinh.md | FixedSizeChunker (`fixed_size`) | 34 | 489.09 | No (Cắt ngang bảng) |
| thongbaotuyensinh.md | SentenceChunker (`by_sentences`) | 39 | 382.79 | Partial |
| thongbaotuyensinh.md | RecursiveChunker (`recursive`) | 44 | 340.43 | Partial |
| phu-luc-01-chi-tieu-dai-hoc-2026.md | FixedSizeChunker (`fixed_size`) | 10 | 459.70 | No |
| phu-luc-01-chi-tieu-dai-hoc-2026.md | SentenceChunker (`by_sentences`) | 1 | 4146.00 | Yes (but too long) |
| phu-luc-01-chi-tieu-dai-hoc-2026.md | RecursiveChunker (`recursive`) | 11 | 377.00 | Partial |
| phu-luc-02-to-hop-mon-ma-bai-thi.md | FixedSizeChunker (`fixed_size`) | 4 | 423.75 | No |
| phu-luc-02-to-hop-mon-ma-bai-thi.md | SentenceChunker (`by_sentences`) | 1 | 1544.00 | Yes |
| phu-luc-02-to-hop-mon-ma-bai-thi.md | RecursiveChunker (`recursive`) | 5 | 309.00 | Partial |
| phu-luc-03-chi-tieu-vb2ca-2026.md | FixedSizeChunker (`fixed_size`) | 5 | 410.60 | No |
| phu-luc-03-chi-tieu-vb2ca-2026.md | SentenceChunker (`by_sentences`) | 1 | 1852.00 | Yes |
| phu-luc-03-chi-tieu-vb2ca-2026.md | RecursiveChunker (`recursive`) | 5 | 370.60 | Partial |
| rag_system_design.md | FixedSizeChunker (`fixed_size`) | 6 | 440.17 | No |
| rag_system_design.md | SentenceChunker (`by_sentences`) | 5 | 476.80 | Yes |
| rag_system_design.md | RecursiveChunker (`recursive`) | 7 | 341.57 | Yes |
| vector_store_notes.md | FixedSizeChunker (`fixed_size`) | 5 | 464.60 | No |
| vector_store_notes.md | SentenceChunker (`by_sentences`) | 8 | 264.12 | Yes |
| vector_store_notes.md | RecursiveChunker (`recursive`) | 7 | 303.29 | Yes |
| customer_support_playbook.txt | FixedSizeChunker (`fixed_size`) | 4 | 460.50 | No |
| customer_support_playbook.txt | SentenceChunker (`by_sentences`) | 4 | 421.50 | Yes |
| customer_support_playbook.txt | RecursiveChunker (`recursive`) | 5 | 338.40 | Yes |

### Strategy Của Tôi

**Loại:** SectionChunker (Custom strategy)

**Mô tả cách hoạt động:**
> Chiến lược này sử dụng ký tự phân tách là `\n## ` (các tiêu đề Markdown cấp 2). Nó coi mỗi đề mục lớn trong thông báo là một đơn vị thông tin hoàn chỉnh.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu tuyển sinh có cấu trúc phân mục rất rõ ràng (I, II, III...). Việc chia theo section đảm bảo các bảng biểu và danh sách điều kiện đi kèm không bị xé lẻ giữa các chunk.

**Code snippet (nếu custom):**
```python
class SectionChunker:
    def chunk(self, text: str) -> list[str]:
        sections = text.split("\n## ")
        chunks = []
        for i, section in enumerate(sections):
            content = ("## " + section.strip()) if i > 0 else section.strip()
            if content: chunks.append(content)
        return chunks
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| thongbaotuyensinh.md | best baseline (Sentence) | 39 | 382.79 | 7/10 |
| thongbaotuyensinh.md | **của tôi (Section)** | 6 | 2494.67 | 9/10 |

### So Sánh Với Thành Viên Khác

| Thành viên         | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|--------------------|----------|----------------------|-----------|----------|
| Nguyễn Hoàng Dương | SectionChunker | 9/10 | Giữ nguyên cấu trúc bảng và các mục điều kiện quan trọng. | Chunk khá dài, có thể chứa thông tin thừa. |
| Thành viên A       | Sliding Window (Small size) | 6/10 | Thu hồi được các từ khóa cụ thể nhanh chóng. | Hay bị mất ngữ cảnh do cắt ngang câu/đoạn. |
| Thành viên B       | Semantic Chunking | 8/10 | Nhóm các ý tương đồng rất tốt về mặt ngữ nghĩa. | Đôi khi tách rời các bảng dữ liệu nếu nội dung đa dạng. |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> **SectionChunker là tốt nhất.** Vì văn bản quy định tuyển sinh của Bộ Công an được trình bày theo cấu trúc phân mục cực kỳ chặt chẽ (Điều 1, Điều 2...). Việc giữ trọn vẹn từng mục giúp Agent trả lời chính xác các câu hỏi tra cứu thông tin cứng mà không bị mất dữ liệu quan trọng nằm trong bảng biểu hoặc danh sách liệt kê.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng biểu thức chính quy `r'.*?[.!?](?:\s+|$)'` để tách văn bản thành các câu. Sau đó, gom nhóm các câu lại dựa trên `max_sentences_per_chunk` để tạo thành các chunk có nghĩa.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Sử dụng thuật toán đệ quy thử các ký tự phân tách theo thứ tự ưu tiên (\n\n, \n, ...). Nếu một đoạn vẫn vượt quá `chunk_size`, nó sẽ tiếp tục bị chia nhỏ bởi ký tự phân tách tiếp theo cho đến khi đạt yêu cầu.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Lưu trữ các tài liệu dưới dạng dictionary gồm nội dung, metadata và vector embedding. Khi tìm kiếm, tính tích vô hướng (dot product) giữa query và tất cả các chunk để tìm ra top_k kết quả có điểm cao nhất.

**`search_with_filter` + `delete_document`** — approach:
> Thực hiện lọc (filter) các bản ghi dựa trên metadata trước khi thực hiện tìm kiếm vector. Việc xóa tài liệu được thực hiện bằng cách lọc bỏ các chunk có `id` trùng khớp khỏi danh sách lưu trữ.

### KnowledgeBaseAgent

**`answer`** — approach:
> Lấy `top_k` chunk liên quan nhất từ store, gộp chúng lại thành một chuỗi context duy nhất. Sau đó, inject context này vào prompt mẫu và gửi cho LLM để sinh câu trả lời.

### Test Results

```
============================= test session starts ==============================
platform darwin -- Python 3.x.x, pytest-8.4.2, pluggy-1.5.0
rootdir: /Users/nhduongss/VinUni Project/Day-07-Lab-Data-Foundations
collected 42 items

tests/test_solution.py ..........................................       [100%]

============================== 42 passed in 0.xxs ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Tổng chỉ tiêu tuyển mới đại học chính quy là bao nhiêu? | 1.870 chỉ tiêu |
| 2 | Có bao nhiêu mã bài thi đánh giá của Bộ Công an? | 04 mã bài thi (CA1, CA2, CA3, CA4) |
| 3 | Thí sinh phía Nam đăng ký trường phía Bắc thì thi ở đâu? | Được tổ chức thi tại phía Nam |
| 4 | Điều kiện chứng chỉ IELTS để xét tuyển Phương thức 2? | IELTS (Academic) đạt từ 5.5 trở lên |
| 5 | Độ tuổi dự tuyển đại học đối với học sinh phổ thông? | Không quá 22 tuổi (dân tộc thiểu số không quá 25 tuổi) |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
