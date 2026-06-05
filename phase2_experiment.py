
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(os.getcwd())))

from src.chunking import ChunkingStrategyComparator
from src.models import Document
from src.store import EmbeddingStore

class SectionChunker:
    """
    Custom strategy for Phase 2.
    Splits text by Markdown headers (##) to keep sections together.
    """
    def chunk(self, text: str) -> list[str]:
        # Split by level 2 headers, keeping the header with the content
        sections = text.split("\n## ")
        chunks = []
        for i, section in enumerate(sections):
            if i == 0:
                content = section.strip()
            else:
                content = "## " + section.strip()
            if content:
                chunks.append(content)
        return chunks

def run_experiment():
    file_path = "data/thongbaotuyensinh.md"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("--- Phase 2: Chunking Strategy Experiment ---")
    
    # 1. Baseline Analysis
    comparator = ChunkingStrategyComparator()
    baseline_results = comparator.compare(text, chunk_size=500)
    
    print("\n[Baseline Results]")
    for name, stats in baseline_results.items():
        print(f"Strategy: {name}")
        print(f"  Count: {stats['count']}")
        print(f"  Avg Length: {stats['avg_length']:.2f}")
        print("-" * 20)

    # 2. Custom Strategy Analysis
    custom_chunker = SectionChunker()
    custom_chunks = custom_chunker.chunk(text)
    
    custom_lengths = [len(c) for c in custom_chunks]
    print("\n[Custom Strategy: SectionChunker]")
    print(f"  Count: {len(custom_chunks)}")
    print(f"  Avg Length: {sum(custom_lengths)/len(custom_chunks):.2f}")
    print(f"  Max Length: {max(custom_lengths)}")
    
    print("\nExample Chunk (First 100 chars):")
    if custom_chunks:
        print(f"'{custom_chunks[1][:100]}...'".replace('\n', ' '))

if __name__ == "__main__":
    run_experiment()
