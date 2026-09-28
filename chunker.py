"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# Every document in campus_life opens with a one-line title — "Noise levels in
# Morrow House", "CS 210 Data Structures — assessment" — and the thing being
# described is named *only* there. Splitting on paragraphs without carrying that
# line forward strands the body: "loud until about 1am on weekends" stops being
# about Morrow House. So the title is detected once and prepended to every chunk
# cut from that document.
TITLE_MAX_CHARS = 80

# Below this, a paragraph is a fragment rather than a thought, so it gets merged
# into its neighbour instead of standing as its own chunk.
MIN_BODY_CHARS = 120


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _paragraphs(text: str) -> list[str]:
    """Split on blank lines, dropping empties."""
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def _looks_like_title(paragraph: str) -> bool:
    """A single short line with no internal break is a heading, not prose."""
    return "\n" not in paragraph and len(paragraph) <= TITLE_MAX_CHARS


def _merge_short(paragraphs: list[str], min_chars: int) -> list[str]:
    """Roll paragraphs together until each one carries a whole thought."""
    merged: list[str] = []
    buffer = ""
    for paragraph in paragraphs:
        buffer = f"{buffer}\n\n{paragraph}" if buffer else paragraph
        if len(buffer) >= min_chars:
            merged.append(buffer)
            buffer = ""
    if buffer:
        # A trailing fragment joins the previous chunk rather than becoming the
        # 2-character chunk the fallback produces on advice_threads.
        if merged:
            merged[-1] = f"{merged[-1]}\n\n{buffer}"
        else:
            merged.append(buffer)
    return merged


def _split_oversize(text: str, limit: int) -> list[str]:
    """Cut on sentence boundaries, never mid-sentence, if a paragraph is long."""
    if len(text) <= limit:
        return [text]

    pieces: list[str] = []
    buffer = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        candidate = f"{buffer} {sentence}".strip()
        if buffer and len(candidate) > limit:
            pieces.append(buffer)
            buffer = sentence
        else:
            buffer = candidate
    if buffer:
        pieces.append(buffer)
    return pieces


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Title-anchored paragraph chunking — the Milestone 3 strategy.

    These documents are short posts, median 305 characters and none over 549,
    so the fallback's 800-character window never cuts anything: 88 documents in,
    88 chunks out. That leaves two or three separate thoughts sharing one chunk
    — noise levels, then laundry, then a recommendation to use the library.

    So: split on paragraph breaks, merge anything under MIN_BODY_CHARS so no
    fragment stands alone, and prepend the document's title line to every piece
    so each chunk still names what it is about. The title is the overlap — it is
    the only context the body paragraphs actually need, and repeating 30
    characters is cheaper than repeating 120 characters of arbitrary prose.
    """
    limit = config.CHUNK_SIZE
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = _paragraphs(doc.text)
        if not paragraphs:
            continue

        if len(paragraphs) > 1 and _looks_like_title(paragraphs[0]):
            title, body = paragraphs[0], paragraphs[1:]
        else:
            title, body = "", paragraphs

        # Leave room for the title we are about to put back on the front.
        room = limit - (len(title) + 2) if title else limit

        pieces: list[str] = []
        for paragraph in _merge_short(body, MIN_BODY_CHARS):
            pieces.extend(_split_oversize(paragraph, room))

        for index, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    text=f"{title}\n\n{piece}" if title else piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
