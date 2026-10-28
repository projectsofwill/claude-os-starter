# Analysis

One folder per question: `analysis/YYYY-MM-DD-<slug>/`.

- `notes.md`: the question (who asked, by when), the source (report link, query, or `revops/queries.md`
  entry), filters and date range, the answer, and the **tie-out**.
- `query.sql` / `query.soql` / `analysis.py`: whatever produced the numbers, so a rerun is one command.
- Raw exports (CSV, XLSX, Parquet) sit next to them and are **gitignored**: they hold customer data, and the
  source system is the truth. Keep the query, not the dump. Finished decks and models live in company Drive;
  link them from `notes.md`.

**Tie-out rule:** before a number leaves this repo, reconcile it to an independent total in the source
system (a CRM report total, a finance figure) and record both in `notes.md`:
`ties to <source> <total> (diff <x>, why)`. No tie-out: label the number "unreconciled".

A query run twice goes into `revops/queries.md`. For Python with packages, `uv run --with pandas analysis.py`
keeps dependencies per script (if `uv` is allowed on the laptop).
