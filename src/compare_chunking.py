from pathlib import Path

from chunking import ChunkingStrategyComparator

DATA_DIR = Path("/Users/nhduongss/VinUni Project/Day-07-Lab-Data-Foundations/data")

comparator = ChunkingStrategyComparator()

for file_path in DATA_DIR.iterdir():

    if file_path.suffix not in [".txt", ".md"]:
        continue

    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    result = comparator.compare(
        text=text,
        chunk_size=500
    )

    print(f"\n{'=' * 50}")
    print(file_path.name)
    print('=' * 50)

    for strategy, stats in result.items():

        print(
            f"{strategy:<15}"
            f" chunks={stats['count']:<4}"
            f" avg_len={stats['avg_length']:.2f}"
        )