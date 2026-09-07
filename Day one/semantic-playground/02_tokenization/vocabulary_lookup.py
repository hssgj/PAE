"""Semantic Playground — Step 2: Vocabulary lookup

Connects tokens to our deliberately small Czech vocabulary.

This is a teaching experiment, not a full morphological analyzer.
A wordform may have more than one possible analysis, so lookup returns
all matching entries instead of silently choosing one.
"""

from pathlib import Path
import csv


VOCABULARY_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "vocabulary" / "cz-mini.tsv"
)


def load_vocabulary(path: Path = VOCABULARY_PATH) -> dict[str, list[dict[str, str]]]:
    """Load the TSV vocabulary, keeping all analyses for each wordform."""
    vocabulary: dict[str, list[dict[str, str]]] = {}

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(
            (line for line in file if not line.startswith("#")),
            delimiter="\t",
        )

        for row in reader:
            wordform = row["wordform"]
            vocabulary.setdefault(wordform, []).append(row)

    return vocabulary


def lookup(token: str, vocabulary: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    """Return every known analysis for a token, or an empty list if unknown."""
    return vocabulary.get(token.lower(), [])


if __name__ == "__main__":
    vocabulary = load_vocabulary()

    examples = ["pes", "může", "je", "drak"]

    for token in examples:
        analyses = lookup(token, vocabulary)
        print(f"TOKEN: {token}")

        if not analyses:
            print("  UNKNOWN")
        else:
            for analysis in analyses:
                print(
                    f"  lemma={analysis['lemma']} "
                    f"category={analysis['category']} "
                    f"role={analysis['role']}"
                )

        print()
