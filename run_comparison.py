
import os
from src.chunking import SentenceChunker

class SectionChunker:
    def chunk(self, text: str) -> list[str]:
        sections = text.split("\n## ")
        chunks = []
        for i, section in enumerate(sections):
            content = ("## " + section.strip()) if i > 0 else section.strip()
            if content: chunks.append(content)
        return chunks

def get_stats(chunks):
    if not chunks:
        return 0, 0
    lengths = [len(c) for c in chunks]
    return len(chunks), sum(lengths) / len(chunks)

files = [
    "data/thongbaotuyensinh.md",
    "data/phu-luc-01-chi-tieu-dai-hoc-2026.md",
    "data/phu-luc-02-to-hop-mon-ma-bai-thi.md",
    "data/phu-luc-03-chi-tieu-vb2ca-2026.md"
]

section_chunker = SectionChunker()
sentence_chunker = SentenceChunker(max_sentences_per_chunk=3)

print(f"| Tài liệu | Strategy | Chunk Count | Avg Length |")
print(f"|---|---|---|---|")

for f_path in files:
    with open(f_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Baseline (Sentence)
    count, avg = get_stats(sentence_chunker.chunk(text))
    print(f"| {os.path.basename(f_path)} | Sentence (Baseline) | {count} | {avg:.2f} |")
    
    # Mine (Section)
    count, avg = get_stats(section_chunker.chunk(text))
    print(f"| {os.path.basename(f_path)} | **Section (Mine)** | {count} | {avg:.2f} |")
