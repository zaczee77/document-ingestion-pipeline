"""Document ingestion pipeline, a small reference demo.

The demo ingests a few invented documents and a small invented
spreadsheet, the way a deal workspace ingests documents before any
question can be answered from them. Each document is split into
chunks, each chunk gets metadata and a content hash, exact duplicate
chunks are dropped, empty chunks are flagged and kept out of the
index, and a small keyword index is built over the chunks that
remain. A lookup then finds chunks by keyword.

Plain Python, no external packages, no network calls.

Run it with: python3 demo/ingestion_demo.py
"""

import hashlib
import re

SAMPLE_DOCS = [
    {
        "id": "DOC1",
        "title": "Harbor quarterly memo",
        "kind": "text",
        "paragraphs": [
            "Harbor revenue in the second quarter was 3.1 million dollars.",
            "Harbor opened 2 new stores in the second quarter, bringing the total to 28 stores.",
            "Harbor hired 12 people in the second quarter, across support and sales.",
        ],
    },
    {
        "id": "DOC2",
        "title": "Harbor pricing sheet",
        "kind": "spreadsheet",
        "rows": [
            {"plan": "Standard", "price": "39 dollars per month", "support": "email support"},
            {"plan": "Premium", "price": "79 dollars per month", "support": "priority support"},
        ],
    },
    {
        "id": "DOC3",
        "title": "Harbor product note",
        "kind": "text",
        "paragraphs": [
            "The loyalty feature launches in June.",
            "Harbor revenue in the second quarter was 3.1 million dollars.",
            "",
        ],
    },
]


def content_hash(text):
    """Short hash of the normalized text, used to spot exact duplicates."""
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]


def chunk_text(doc):
    """Split one document into raw chunks, one per paragraph or row."""
    chunks = []
    if doc["kind"] == "text":
        for number, paragraph in enumerate(doc["paragraphs"], start=1):
            chunks.append(
                {
                    "source": doc["id"],
                    "title": doc["title"],
                    "kind": "text",
                    "number": number,
                    "text": paragraph,
                }
            )
    else:
        for number, row in enumerate(doc["rows"], start=1):
            text = (
                "Plan "
                + row["plan"]
                + ", price "
                + row["price"]
                + ", support "
                + row["support"]
                + "."
            )
            chunks.append(
                {
                    "source": doc["id"],
                    "title": doc["title"],
                    "kind": "row",
                    "number": number,
                    "text": text,
                }
            )
    return chunks


def ingest(docs):
    """Run the pipeline: chunk, hash, dedupe, flag, index.

    Returns a dict with the chunk lists at each stage plus the index.
    A chunk is kept in the index only when it has text and is not a
    duplicate of a chunk seen earlier. The first copy of a repeated
    chunk is the one kept, so the citation still points at a real
    source.
    """
    raw = []
    for doc in docs:
        raw.extend(chunk_text(doc))

    for chunk in raw:
        chunk["hash"] = content_hash(chunk["text"])

    kept = []
    duplicates = []
    seen_hashes = set()
    for chunk in raw:
        if chunk["hash"] in seen_hashes:
            duplicates.append(chunk)
        else:
            seen_hashes.add(chunk["hash"])
            kept.append(chunk)

    flagged = []
    indexed = []
    for chunk in kept:
        if not chunk["text"].strip():
            flagged.append((chunk, "empty chunk"))
        else:
            indexed.append(chunk)

    index = {}
    for position, chunk in enumerate(indexed):
        words = set(re.findall(r"[a-z0-9]+", chunk["text"].lower()))
        for word in words:
            index.setdefault(word, []).append(position)

    return {
        "raw": raw,
        "kept": kept,
        "duplicates": duplicates,
        "flagged": flagged,
        "indexed": indexed,
        "index": index,
    }


def lookup(result, term):
    """Return the indexed chunks that contain the term."""
    positions = result["index"].get(term.lower(), [])
    return [result["indexed"][position] for position in positions]


def main():
    result = ingest(SAMPLE_DOCS)

    print("Documents ingested: " + str(len(SAMPLE_DOCS)))
    print("Raw chunks: " + str(len(result["raw"])))
    print("Duplicates dropped: " + str(len(result["duplicates"])))
    for chunk in result["duplicates"]:
        print(
            "  Duplicate dropped from "
            + chunk["source"]
            + ", chunk "
            + str(chunk["number"])
            + ": "
            + chunk["text"]
        )
    print("Empty chunks flagged: " + str(len(result["flagged"])))
    for chunk, reason in result["flagged"]:
        print(
            "  Flagged in "
            + chunk["source"]
            + ", chunk "
            + str(chunk["number"])
            + ": "
            + reason
        )
    print("Chunks in the index: " + str(len(result["indexed"])))
    print()

    for term in ["revenue", "price", "loyalty", "churn"]:
        hits = lookup(result, term)
        print("Lookup '" + term + "': " + str(len(hits)) + " chunk(s)")
        for chunk in hits:
            print(
                "  ["
                + chunk["source"]
                + ", chunk "
                + str(chunk["number"])
                + "] "
                + chunk["text"]
            )
    print()

    print(
        str(len(SAMPLE_DOCS))
        + " documents, "
        + str(len(result["raw"]))
        + " raw chunks, "
        + str(len(result["duplicates"]))
        + " duplicate dropped, "
        + str(len(result["flagged"]))
        + " empty chunk flagged, "
        + str(len(result["indexed"]))
        + " chunks indexed."
    )

    # Built in checks: every stage keeps the counts the sample data
    # was written to produce, every indexed chunk carries metadata and
    # a hash, and every lookup returns only chunks that contain the term.
    assert len(result["raw"]) == 8
    assert len(result["duplicates"]) == 1
    assert len(result["flagged"]) == 1
    assert len(result["indexed"]) == 6
    for chunk in result["indexed"]:
        assert chunk["source"] and chunk["title"] and chunk["kind"]
        assert chunk["text"].strip()
        assert len(chunk["hash"]) == 8
    assert len(lookup(result, "revenue")) == 1
    assert len(lookup(result, "price")) == 2
    assert len(lookup(result, "loyalty")) == 1
    assert len(lookup(result, "churn")) == 0
    for chunk in lookup(result, "revenue"):
        assert "revenue" in chunk["text"].lower()
    print("All checks passed.")


if __name__ == "__main__":
    main()
