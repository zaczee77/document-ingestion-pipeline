# Demo: document ingestion pipeline

A small reference demo of the ingestion step behind Txvni: documents and spreadsheet rows are split into chunks, each chunk gets metadata and a content hash, exact duplicates are dropped, empty chunks are flagged and kept out of the index, and a keyword index is built over the chunks that remain.

## How to run it

From the repository root, or from this folder:

```
python3 demo/ingestion_demo.py
```

Plain Python, no external packages, no network calls.

## What it does

1. It ingests 3 invented documents: a quarterly memo with 3 paragraphs, a pricing sheet with 2 spreadsheet rows, and a product note with 3 paragraphs.
2. It splits them into 8 raw chunks, one per paragraph or row, and gives each chunk a source id, a title, a chunk number, a kind, and a short hash of its normalized text.
3. It drops 1 duplicate: the product note repeats the revenue paragraph from the quarterly memo word for word, so the second copy is dropped and the first copy is kept.
4. It flags 1 empty chunk: the last paragraph of the product note is blank, so it is reported as flagged and kept out of the index.
5. It indexes the 6 chunks that remain, then runs four lookups. Revenue finds 1 chunk, price finds 2 chunks, loyalty finds 1 chunk, and churn finds 0 chunks, which is the correct result when no document mentions churn.

## What it printed when it was tested

3 documents, 8 raw chunks, 1 duplicate dropped, 1 empty chunk flagged, 6 chunks indexed. The built in checks passed: the counts match the sample data, every indexed chunk carries metadata and a hash, and every lookup returns only chunks that contain the term.

## What the sample data is

Every document title, paragraph, company name, amount, price, and date in `ingestion_demo.py` is invented sample data written only to exercise the pattern. Nothing here is a real document, a real deal, a real price, or a real model output. A real system would run its ingestion against real documents. None of those are modeled here.

## Files

1. `ingestion_demo.py`: the demo. The document set, the chunking, the dedupe and flagging steps, the keyword index, the lookups, and the built in assertions.
2. `README.md`: this file.
