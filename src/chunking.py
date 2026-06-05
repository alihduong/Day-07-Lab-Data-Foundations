from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        return [text[i : i + self.chunk_size] for i in range(0, len(text), step) if i < len(text)]


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        
        # Regex explanation:
        # Match anything lazily followed by a punctuation mark ([.!?])
        # which is followed by either whitespace (\s+) or the end of the string ($).
        # DOTALL allows the '.' to match newline characters.
        sentence_pattern = r'.*?[.!?](?:\s+|$)'
        sentences = re.findall(sentence_pattern, text, flags=re.DOTALL) or [text]
        
        # Capture any remaining text that didn't end with punctuation
        last_match_end = sum(len(s) for s in sentences)
        if last_match_end < len(text):
            remaining = text[last_match_end:].strip()
            if remaining:
                sentences.append(remaining)

        return [
            "".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            for i in range(0, len(sentences), self.max_sentences_per_chunk)
            if "".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
        ]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        return self._split(text, self.separators)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        if not separators:
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        sep = separators[0]
        next_seps = separators[1:]
        
        if sep == "":
            return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]

        parts = text.split(sep)
        chunks, current_chunk = [], []
        current_len = 0

        for i, part in enumerate(parts):
            # Re-attach separator to all parts except the last one
            item = part + sep if i < len(parts) - 1 else part
            item_len = len(item)

            if item_len > self.chunk_size:
                if current_chunk:
                    chunks.append("".join(current_chunk))
                    current_chunk, current_len = [], 0
                chunks.extend(self._split(item, next_seps))
            elif current_len + item_len <= self.chunk_size:
                current_chunk.append(item)
                current_len += item_len
            else:
                if current_chunk:
                    chunks.append("".join(current_chunk))
                current_chunk, current_len = [item], item_len

        if current_chunk:
            chunks.append("".join(current_chunk))

        return [c for c in chunks if c]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(x * x for x in vec_b))
    
    if mag_a == 0 or mag_b == 0:
        return 0.0
        
    return _dot(vec_a, vec_b) / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size)
        }
        
        comparison = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            lengths = [len(c) for c in chunks]
            
            comparison[name] = {
                "count": len(chunks),
                "avg_length": sum(lengths) / len(chunks) if chunks else 0.0,
                "max_length": max(lengths) if chunks else 0,
                "chunks": chunks
            }
            
        return comparison
