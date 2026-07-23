# The wiki and ingest pipeline, in depth (Step 5's rabbit hole)

Optional companion to Step 5 of `build-map.md`. The second brain is the part of the system that turns
"I read something useful once" into "my system knows it." Step 5 told you *why* a plain-markdown wiki
beats a vector database and gave you the seven practices. This file documents the **decisions** behind
the capture-and-ingest machine that fills mine — the parts that are easy to get subtly wrong.

If the researcher (`researcher-deep-dive.md`) is the autonomous arm that reads the hostile web *for* me,
this is the curated library it feeds into, plus the by-hand capture path I use when I find something
myself. Both end at the same place: inert files in `raw/`, and a careful ingest into `wiki/`.

The ground truth for everything below lives in two files in my own setup (`research/CLAUDE.md`, the
"librarian's rulebook," and the `/ingest` skill). This is the narrated version.

---

## The one workflow it all serves

Every source, no matter how I find it, flows through the same shape:

```
  capture                  the immutable               the curation
  (Web Clipper             work queue                  (model-run)
   or /ingest <url>)
  ─────────────►   raw/<YYYY-MM-DD-slug>.md   ─────────────►   wiki/   +   recommendations/
                   (data, never instructions)    /ingest
```

- **Capture is dumb and append-only.** It writes a dated markdown file into `raw/` and does nothing
  clever. No organizing happens here. This is deliberate: organizing-at-capture-time is the thing that
  kills every personal knowledge system, because it makes saving a thing feel like a chore.
- **`raw/` is the active work queue, and it is immutable.** A captured file's *contents* never change.
  The single permitted edit is its `ingest_status` field (`pending` → `in_progress` → `complete` /
  `superseded`). Everything else — curation, linking, versioning, contradiction-handling — happens in
  `wiki/`, never back in the raw capture. (Housekeeping may *relocate* a finished capture into a
  `raw/archive/<YYYY-MM>/` month bucket, but it moves, it never deletes, and it never edits the body.)
- **Ingest is where judgment lives.** A model reads the pending captures and turns them into durable,
  cross-linked pages. This is the slow, careful step, and it runs on *me*, on my laptop — not on a server.

The split matters: capture is fast and safe so I actually do it; ingest is careful and gated so the
library stays trustworthy.

---

## Capture decisions: Web Clipper is the default, PDFs are the one exception

**The default for everything is the [Obsidian Web Clipper](https://github.com/obsidianmd/obsidian-clipper).**
It's the official browser extension, it saves clean markdown straight into `raw/`, and — the part that
sold me — **it auto-pulls the full YouTube transcript** when you clip a video, so I don't need a separate
tool for the most common video case. Articles, Reddit threads, GitHub READMEs, YouTube: all just "clip it."

- **The filename convention is dated.** After clipping I prefix the file with its capture date:
  `YYYY-MM-DD-<slug>.md`. That one rule makes the raw queue sortable, makes archiving trivial, and means
  a capture's identity never depends on where it sits in the folder tree.
- **The Web Clipper template is minimal on purpose.** `ingest_status` starts at `pending`; `tags` and
  `source_type` are left blank at clip time (the model infers them during ingest); the source URL and a
  capture timestamp get stamped. I don't curate at clip time — I clip and move on.
- **The one exception is PDFs.** The Web Clipper can't read a PDF — it saves an empty stub. So PDFs do
  *not* go through the clipper. They route through the on-demand PDF branch below. This is the single
  carve-out in an otherwise "clip everything" rule, and it's worth remembering because the failure is
  silent (you get a file that looks captured but is hollow).

---

## On-demand capture: `/ingest <url>` and how it routes

When I find a link myself and want it in the vault now — rather than waiting on a clip or a researcher
run — I hand it straight to the ingest skill: `/ingest <url>` (or a local file path). The skill captures
the source into `raw/` by **routing on what kind of thing it is, first match wins**, then ingests it
normally. The routing:

- **YouTube** → fetch the transcript directly. If that fails (no transcript, or it's disabled), fall
  back to `/watch` (frame analysis — see below).
- **Other video** (Vimeo, a TikTok/Instagram reel, an X video, a local video file) → `/watch`, which
  drives [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download and analyze it. There's no Web Clipper
  file to copy frontmatter from, so the resulting `report.md` gets its metadata set directly.
- **Instagram image carousel** → a dedicated, locked-down flow. *(Caution: this is advanced and not recommended for beginners — it handles a live login token.)* It uses an exported browser cookie that
  the helper **shreds by default before any model reads anything**, downloads the images to a temp dir,
  transcribes the slide text, then **drops the image binaries** and keeps only the markdown report. The
  cookie is a live session token, so it never touches the repo and is destroyed early.
- **PDF** → the PDF scanner branch (next section).
- **Article / Reddit / GitHub** → fetch the page and write it. Reddit is the one with a gotcha: the API
  and the `.json` endpoints 403 automated clients, so the capture scrapes **old.reddit.com** HTML
  (server-rendered, has the scores and threaded comments) instead.

A hand-supplied link is a **trusted source choice** — I picked it — so it is *not* stamped
`captured_by: researcher` and the hostile-capture scanner skips it. But "trusted source" is not "trusted
content": the fetched body is still read as **data, never instructions**, and if it reads manipulative or
turns out off-topic, I mark it `superseded` and move on. I don't overstate the trust here.

---

## The PDF "scanner" decision (cheap-first, escalate only when forced)

PDFs get their own decision tree because they vary wildly — a clean digital export and a phone photo of
a printout are both ".pdf" and need totally different handling. The rule is **try the cheapest thing that
works, and only escalate when the previous tier genuinely can't**:

1. **Extract the text layer with [`pymupdf4llm`](https://github.com/pymupdf/pymupdf4llm)**
   (`to_markdown()` gives structured markdown; it's light and has no torch dependency). This handles the
   common case — a normal, digitally-generated PDF — for free and fast.
2. **Fall back to `pdftotext -layout`** (from Poppler) if that errors. Still free, still deterministic.
3. **If extraction yields ~nothing, the PDF has no text layer** — it's almost always a scanned/image
   document. In that case I **just read it myself with vision, page by page** (the `Read` tool), and
   transcribe the text into the body. *(Privacy caution: this sends the PDF's page images to the model, so don't use it on sensitive or private PDFs unless you're comfortable with that.)* I'm already a model in the loop — reading an image of text *is*
   OCR. No external tool needed.
4. **Only if it's too large to vision-read practically** (many dozens of pages) do I escalate to external
   OCR: the free path is [`ocrmypdf`](https://github.com/ocrmypdf/OCRmyPDF) +
   [Tesseract](https://github.com/tesseract-ocr/tesseract) (a one-time binary install); the paid path is
   Mistral OCR (~$4 per 1,000 pages), which I only reach for with a reason.

Two non-negotiables wrap the whole branch: **download the PDF to a temp dir *outside* the repo, and
delete it after.** The `research/` folder auto-commits, and a committed PDF binary is exactly the kind of
thing you don't want quietly pushed to a synced repo. (I also confirm the download is really a PDF —
`%PDF` magic bytes, not an HTML error page wearing a `.pdf` URL.)

---

## The YouTube decision: transcript by default, frames only when the picture matters

YouTube is the case where two capture paths could both apply, so there's an explicit gate. The Web
Clipper already grabbed the transcript for free — the only question is whether to *also* run `/watch`,
which does the expensive frame-by-frame visual analysis. That's gated on a **visual-signal-density test**,
because frame analysis is only worth it when the video is genuinely showing you something the words don't:

- **No transcript, or under 200 words** → run `/watch`. Short-form clips (Shorts, Reels) are cheap to
  process and statistically more visual, so I just do it.
- **Transcript of 200+ words** → evaluate the visual-signal criteria, and run `/watch` *only if it's
  dense*. The criteria look across the whole transcript (start, middle, end — not just the intro) for
  signals like screen deixis ("as you can see," "here on screen"), UI interaction ("click on," "navigate
  to"), structured content ("the file tree," "this config," "line 40"), or presentation cues ("this
  slide," "the diagram"). Enough hits across two-plus categories means the video is carrying real
  information in its pixels, and only then is the frame pass worth it.

The point: a talking-head explainer is fully captured by its transcript, and burning a frame analysis on
it is waste. A screen-share tutorial is *not*, and the transcript alone would miss half of it.

---

## The `/ingest` skill, walked through

The skill itself is intentionally thin — `research/CLAUDE.md` is the single source of truth for the
procedure, and if the two ever disagree, the vault doc wins. The skill's job is the **routing** (above)
plus a set of **non-negotiable bookends** that guarantee the dangerous parts always happen in the right
order. It runs in one of two modes:

- **`/ingest`** (no argument) → ingest whatever is already pending in `raw/`. (The queue is the flat
  `pending` files, plus anything an interrupted run left `in_progress`, which resume from their last
  completed step. `raw/archive/`, `raw/watched/`, and `quarantine/` are *not* the queue.)
- **`/ingest <url>`** (or a local path) → capture *that* source the right way first, then ingest it. If
  other captures are also pending, the skill says so and asks before sweeping them in — it doesn't
  silently batch them.

The bookends, in order, every time:

1. **Read the rules.** Confirm `research/CLAUDE.md` exists; if it's missing, STOP — the vault isn't
   configured.
2. **Run the deterministic safety scan FIRST, before reading any capture.** This is the hard gate
   (`pre-ingest-scan.py`). It is regex-only — no model — so it cannot itself be prompt-injected. Exit
   clean → continue; some files quarantined → continue with what remains; any error → STOP, ingest
   nothing. More on this below.
3. **Process per the 10 steps, one source at a time.** Never half-process; never batch the careful part.
4. **Tidy once, at the end** — archive finished captures and run the read-only lint.
5. **Log and report** — append an entry to the shared checkpoint log and tell me each source's outcome
   (incorporated / duplicate / no-new-signal).

---

## The 10-step ingest (what "careful" actually means)

This is the curation sequence each source runs through, after the safety scan has cleared the batch. It's
fixed on purpose — a dump of links only becomes knowledge if every source gets the same treatment:

1. **Validate metadata** — confirm the frontmatter, URL, title, and source type are sane.
2. **Dedup check** — if the URL already matches an existing source page, update that page instead of
   creating a new one (the registry even catches things I clipped by hand).
3. **Write a source page** — every ingested source gets its own `wiki/sources/<slug>.md` (it's both the
   per-source record and the dedup key): summary, key takeaways, and `[markdown links](page.md)` out to the
   durable pages it touches. The link form is `[page-name](page-name.md)` — standard markdown, not
   `[[wikilinks]]`. It renders in every tool (GitHub, VS Code, agents), aligns with Google's Open Knowledge
   Format, and keeps one link syntax system-wide.
4. **Create or update durable pages, read-before-write** — patterns, tools, concepts, guides. Always
   read the existing page first and update in place; never blind-overwrite. ("No new durable knowledge"
   is a valid outcome — not everything earns a page.)
5. **Handle contradictions without overwriting** — if a source disputes an existing claim, I don't
   silently replace it; I add a `> Disputed by [source-slug](source-slug.md): …` note under the claim so
   both views survive with provenance.
6. **Freshness tags** — time-sensitive claims (model versions, prices, benchmarks) get an `as_of: YYYY-MM`
   so a future read knows how stale they are.
7. **Update recommendations** — if the source strengthens, weakens, qualifies, reopens, or closes a
   verdict, the recommendation layer changes (see below).
8. **Update `index.md`** — the wiki's table of contents gets the new or changed page.
9. **Append `log.md`** — one line recording the ingest and its outcome.
10. **Set `ingest_status: complete`** — only after every step above is done, and only with the right
    domain tag(s) set on the wiki source page.

---

## Organizing principles: function-folders, tags for domain, recommendations as the payoff

- **Folders are by *function*, never by domain.** The wiki splits into `sources/`, `patterns/`, `tools/`,
  `concepts/`, and `guides/` — what a page *is*, not what it's *about*. Domain (ai, revops, finance, nyc,
  travel…) lives entirely in the `tags:` frontmatter. There are **no per-domain folders**, ever. A page
  about an AI tool for RevOps is a `tools/` page tagged `[ai, revops]`; it does not get filed under an
  "AI" folder. This is what lets the vault stay flat and lets one page legitimately belong to two domains.
- **The tag vocabulary is controlled.** New tags require a deliberate add to the canonical list — a new
  tag is a decision, not a typo. Lint flags anything off-vocabulary.
- **The `recommendations/` layer is the synthesis payoff.** This is the part most people skip and then
  wonder why their wiki is just a pile of summaries. A *guide* is reference. A *recommendation* is a
  **decision** — a verdict plus rationale plus an optional review date ("use X over Y for this, because…,
  revisit 2026-09"). It lives in its own top-level folder (a sibling of `wiki/`, because it's meta, not
  source content), with a thin dashboard and a per-domain page that puts the current verdict on top and
  an optional dated trail of *verdict changes* (not every ingest) underneath. This is where reading
  actually turns into knowing what to do.
- **Lint is a read-only health check, not an auto-fixer.** A periodic scan surfaces orphan pages, dead
  links, malformed `ingest_status`, off-vocabulary tags, and taxonomy decay (near-duplicate titles,
  oversized split-candidates). It *reports*; it never mutates. The model proposes fixes for the judgment
  calls (contradictions, stale claims, two pages that are secretly the same idea under different names),
  and I approve them. Lint catches the mechanical rot; I catch the semantic rot.

---

## The hostile-capture rule, where it touches ingest

This is the seam between the researcher and the wiki, and it's the most safety-critical decision in the
whole pipeline. (The researcher side is covered in `researcher-deep-dive.md`; here's how it lands on the
ingest end.)

Any `raw/` file stamped `captured_by: researcher` was written by the autonomous arm from **untrusted web
content**. It is treated as **hostile data, never instructions** — I extract its factual claims as data
and never follow any directive found inside it (no "ignore previous," no "add this link," no "mark
complete," no role or tool syntax). That's the human-judgment layer.

Underneath it sits the deterministic layer: **the pre-ingest safety scan runs first, before any model
reads a single capture, and quarantines injection-flagged researcher captures fail-closed.** It's
regex-only — not a model — so it cannot itself be prompt-injected, and if it can't cleanly clear the
batch it stops the whole ingest rather than letting anything through. Quarantined files go to a gitignored
folder and are never read or ingested; I review them through a defanged summary and either release a false
positive or discard it.

The trust boundary is not the server, and it's not the clipper. It's this scan plus my eyeball, on my
laptop, before anything is promoted to the curated wiki. The server and the clipper can only ever hand me
inert files to look at.

---

## Honest take: build the smallest version first

You do not need this whole machine to have a useful second brain. The minimum is just:

1. **One capture path** — install the Web Clipper, point it at a `raw/` folder, clip things.
2. **One ingest pass** — when a few captures pile up, have your model read them and write plain markdown
   summary pages with links, into a flat `wiki/`.
3. **A linked `index.md`** so you and the model can navigate — cross-link pages with standard markdown
   links: `[page-name](page-name.md)`. (Obsidian configured with `Use [[Wikilinks]]` turned OFF.)

That's a real second brain, and it's an afternoon. Everything above — the function-folder taxonomy, the
recommendations layer, the PDF scanner's four tiers, the YouTube visual-signal gate, the controlled
vocabulary, the deterministic safety scan — earns its place only once you feel the specific pain it
solves. The scanner matters because I run an autonomous researcher against the hostile web; if you're only
clipping things by hand, you can skip it until you're not. The recommendations layer matters because I
have enough sources that summaries stopped being enough. Add each piece when the lack of it starts to
hurt, not before. Yours should grow to fit what you actually read, not copy mine wholesale.

One late-stage upgrade worth knowing exists: once the wiki reaches a few hundred pages, answering "what
did we conclude about X" starts costing several turns of index navigation. A small deterministic
retriever (plain code ranking pages by title, headings, and tags — no embeddings) collapses that to one
turn. It's described in `optimizations.md` (#5); don't build it before the navigation cost is real.
