# Document ingestion pipeline

A reference pattern and a small runnable demo for taking documents and spreadsheets into a system before any question can be answered from them. The pattern comes from work Nirmeet Rao has shipped: Txvni, his AI deal workspace for private equity, hedge fund, and family office teams, which ingests documents and spreadsheets for cited question answering, KPI extraction, risk analysis, benchmarks, IC memos, collaboration, and audit trail.

## The problem

A question answering system is only as honest as the documents it was fed. If ingestion silently drops a page, keeps two copies of the same paragraph, or files a chunk with no record of where it came from, every answer built on top of it inherits that damage. A citation that points at a chunk nobody can trace back to a source document is decoration, and a duplicate chunk counted twice can make a single passage look like two independent pieces of evidence.

Ingestion is the unglamorous step that decides whether the rest of the system can be trusted. It runs before retrieval, before ranking, and before any answer is written. Get it right and the later steps have clean material to work with. Get it wrong and no amount of careful answering can repair it.

## What the pattern does

1. Every document is split into chunks, one per paragraph for text and one per row for a spreadsheet, so that a later citation can point at a single chunk.
2. Every chunk gets metadata: the source document, the document title, the chunk number, the kind of chunk, and a short hash of its normalized text.
3. Exact duplicate chunks are dropped, keeping the first copy, so the same passage never enters the index twice.
4. Empty chunks are flagged and kept out of the index, so a lookup never returns a blank result.
5. A small keyword index is built over the chunks that remain, mapping each word to the chunks that contain it, so a lookup returns only chunks that actually contain the term.

## The demo in this repository

The demo folder contains a small reference demo in plain Python with no external packages. It ingests three invented documents: a quarterly memo, a pricing sheet given as spreadsheet rows, and a product note that repeats one paragraph from the memo and ends with an empty paragraph. Out of 8 raw chunks, 1 duplicate is dropped, 1 empty chunk is flagged, and 6 chunks reach the index. A lookup for revenue finds 1 chunk, a lookup for price finds 2 chunks, a lookup for loyalty finds 1 chunk, and a lookup for churn finds nothing, which is the correct result when no document mentions churn.

The docs folder describes the pattern in full: the chunking step, the metadata every chunk carries, the dedupe rule, the flagging rule, and the index that lookups run against.

## What this is not

This demo is not the Txvni product. It models the ingestion step Txvni uses, at miniature scale, with invented sample data. No real documents, deals, or model outputs appear here, and no accuracy, retrieval, or outcome number is claimed. A real system would replace the keyword index with real retrieval over real ingested documents, and would add the steps this demo does not model, such as parsing real file formats, resolving conflicting versions of the same document, handling near duplicates that differ by a word or two, and checking chunk boundaries against tables and figures. None of those are modeled here.

## Links

1. Portfolio: https://nirmeetrao.com
2. GitHub: https://github.com/Zaczee77
3. LinkedIn: https://www.linkedin.com/in/nirmeet-rao
