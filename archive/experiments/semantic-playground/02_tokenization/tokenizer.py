"""Semantic Playground — Step 1: Tokenization

A deliberately simple tokenizer for our experiments.

This is NOT intended to reproduce an LLM tokenizer.
Its purpose is to make the first transformation visible:

    raw text -> tokens

We keep punctuation as separate tokens for now so that we can observe it.
"""

import re


TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Split text into simple word/punctuation tokens."""
    return TOKEN_PATTERN.findall(text)


if __name__ == "__main__":
    example = "Zjisti mi, jestli pes může jíst ostružiny."

    print("RAW INPUT:")
    print(example)
    print("\nTOKENS:")
    print(tokenize(example))
