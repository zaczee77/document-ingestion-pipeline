# The document ingestion pattern

## Where the pattern comes from

Txvni is an AI deal workspace built by Nirmeet Rao and presented on his portfolio at nirmeetrao.com. Its own description says it ingests documents and spreadsheets for cited question answering, KPI extraction, risk analysis, benchmarks, IC memos, collaboration, and audit trail. Ingestion is the first item in that list, and it has to come first in the system too. The cited answering pattern from the companion repository decides what an answer may contain. This pattern decides what material the answering step gets to work with.

A deal workspace, a prior authorization file, or a billing review all face the same ingestion problem. Documents arrive in different shapes, some pages repeat, some rows are blank, and a chunk that cannot be traced back to its source is a liability the moment someone asks where an answer came from.

## The pipeline

A document enters, it is split into chunks, each chunk gets metadata and a hash, duplicates are dropped, empty chunks are flagged, and the chunks that remain go into an index. A lookup then runs against that index, and only against that index. Nothing reaches the answering step except through the index, so nothing unindexed can ever be cited.

Each chunk carries its source document id, the document title, the chunk number inside that document, the kind of chunk, and a short hash of its normalized text. The hash is what makes dedupe possible, and the source id plus chunk number is what makes a citation checkable. A citation names a chunk, and the chunk names its document.

## The five steps

1. Chunking. Text is split one chunk per paragraph. A spreadsheet is split one chunk per row, with the row rendered as a short sentence naming each column. A chunk is the smallest unit that can be cited, so the split decides how precise every later citation can be. Too large and a citation points at a wall of text. Too small and a claim needs several citations to say one thing.
2. Metadata. Every chunk records where it came from before anything else happens to it. Metadata is attached at ingestion time, never reconstructed later, because reconstruction guesses. A chunk with no source is not a chunk. It is a sentence with no provenance, and it does not enter the index.
3. Dedupe. The hash of the normalized text identifies exact duplicates. When the same paragraph appears in two documents, the first copy is kept and the later copies are dropped, with the drop recorded. Keeping both copies would let one passage count as two pieces of evidence. Dropping the first copy instead of the later one would break the citation that points at the original document.
4. Flagging. A chunk that is empty after trimming is flagged and kept out of the index. It is not deleted, because the record of what was skipped is part of the audit trail. It is simply never returned by a lookup, so a search can never surface a blank result. In a real system the same flagging step would also catch chunks that are too short to be useful or that failed to parse, and those would be flagged the same way.
5. Indexing. The surviving chunks go into a keyword index that maps each word to the chunks containing it. A lookup returns only chunks that contain the term, and each returned chunk carries its source and number, so the path from a lookup result back to the original document is one step.

## Design principles

1. Nothing unindexed can be cited. The index is the only door into the answering step. If a chunk did not pass dedupe and flagging, it is not in the index, and no answer can ever quote it.
2. The first copy wins. When two documents contain the same paragraph, the copy that arrived first is kept. Citations stay stable, and the same passage never appears twice.
3. A dropped chunk is recorded, not erased. The pipeline reports every duplicate dropped and every empty chunk flagged, with the source and chunk number. An ingestion run that silently discards material cannot be audited.
4. Metadata is attached at ingestion, never rebuilt. Source, title, number, kind, and hash are written when the chunk is created. Anything reconstructed later is a guess about provenance, and provenance is not something to guess about.
5. A lookup that finds nothing is a correct result. When no chunk contains the term, the lookup returns an empty list. That empty result is information. It tells the answering step the documents do not cover the question, which is exactly what the grounded answering pattern needs to hear.

## What the demo shows, and what it does not show

The demo in this repository shows the pattern at miniature scale: three invented documents, eight raw chunks, one duplicate dropped, one empty chunk flagged, six chunks indexed, and four lookups. It shows the shape of the work: chunking, metadata, dedupe, flagging, and a lookup that returns only chunks that contain the term. It does not show real documents, real file parsing, real retrieval, or measured results, and it does not show the Txvni product. Real parsing of PDFs and spreadsheets, real handling of near duplicates, real version conflicts between copies of the same document, and real chunk boundary decisions around tables and figures are all real parts of an ingestion system, and none of them are modeled in the demo. The demo is a reference implementation of the pattern, written in plain Python with no external packages.

## Links

1. Portfolio: https://nirmeetrao.com
2. GitHub: https://github.com/Zaczee77
3. LinkedIn: https://www.linkedin.com/in/nirmeet-rao
