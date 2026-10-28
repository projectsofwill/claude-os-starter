# Meetings

- `raw/`: transcripts and recorder exports (`YYYY-MM-DD-<slug>.md|txt`). **Gitignored**: raw transcripts
  never get committed. Prefer the recorder's own summary export when it has one.
- `YYYY-MM-DD-<slug>.md`: processed notes written by `/meeting-ingest` (summary, decisions, action items,
  metrics, open questions). These are committed.

Run `/meeting-ingest today` at end of day. It's idempotent: a raw file already referenced by a note's
`source:` line is skipped.

**Before recording anything:** check the company's recording and AI-notetaker policy. Some US states require
every participant's consent, and external calls (customers, candidates) often have separate rules.
