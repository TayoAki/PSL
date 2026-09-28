# Test plan — Demo Hub

How we prove each part of the demos hub works: at build time, in CI, after deploy, and every week
it runs. It assumes the stack recommended in
[03-build-plan.md](03-build-plan.md): an Astro Starlight static site with data-driven weekly pages
and a TypeScript drafting pipeline that uses the Claude API. Section 9 covers what changes if we
go with Mintlify instead, and section 10 what changes if we adopt the TypeSafe option for tags
and sensitive flags.

## 1. Principles

1. **Most defects will be content defects.** Wrong date, broken video ID, unknown presenter, tag
   typo, a missing week in the feed. So data validation is the first and cheapest gate, and it
   runs on every PR.
2. **Test the built site, not a dev server.** The site is static. Feeds, search (Pagefind), sitemap
   and markdown exports only exist after `astro build`, so build-output tests and E2E tests run
   against `dist/` (served by `astro preview`).
3. **No live third parties in PR CI.** YouTube and the Claude API are mocked with recorded fixtures.
   YouTube player requests are stubbed in Playwright. Live calls only happen in scheduled jobs and
   in the weekly drafting run.
4. **LLM output is tested two ways.** Deterministic assertions (schema, length, taxonomy, PII)
   block merges. Model-graded quality evals track drift, and run when prompts or models change.
5. **Humans stay in the loop.** Every generated week arrives as a PR. The review checklist is part
   of the test plan.

## 2. Fixtures

`tests/fixtures/` holds **synthetic** content (never Omni's), designed to hit edge cases:

| Fixture | Why |
|---|---|
| `week-typical` (17 demos) | Median 2026-scale page |
| `week-huge` (40 demos) | Performance budget and TOC length (Omni peaked at 34) |
| `week-single` (1 demo) | Singular wording, layout with no TOC scroll |
| `week-holiday` (dated Monday) | Non-Friday dates must still work |
| `week-draft` (`draft: true`) | Must not appear in production build, feed or sitemap |
| `week-unicode` | Non-ASCII titles and names → slugs, anchors, feed escaping, OG image text |
| `week-long-text` | 120-character titles, 150-word summary → layout and truncation rules |
| `week-missing-transcript` | Optional fields missing |
| `year-boundary` (Dec 26 → Jan 2) | Year archives, sidebar grouping and "latest" logic across years |
| YouTube API responses (`playlistItems`, `videos`) | Recorded JSON for pipeline unit tests |
| Transcripts (`*.vtt`, `*.txt`) plus reference summaries | Golden set for LLM evals (section 6) |

## 3. Test layers

### 3.1 Static checks — every PR, < 1 min
- `astro check` and `tsc --noEmit` (strict), ESLint, Prettier `--check`.
- markdownlint on `docs/**`. Optional: Vale with a small style guide for summaries (no
  superlatives, third person).
- gitleaks secret scan.

### 3.2 Content validation — every PR, < 30 s
**Schema (fails the build):** Zod schemas in `src/content.config.ts` for `weeks`, `people` and `tags`.
Astro validates every data file during `astro sync` and `astro build`. Wrong types, unknown
fields, a bad date format or a malformed video ID (`/^[\w-]{11}$/`) fail CI with a file and field
path.

**Invariants (Vitest over all data files).** These are the rules a schema can't express:

| # | Rule | Severity |
|---|---|---|
| C1 | File path matches the date (`demos/2026/2026-09-25.yaml` ⇔ `date: 2026-09-25`) | error |
| C2 | Only one week per date | error |
| C3 | No YouTube video ID appears twice in the archive (unless `reused: true`) | error |
| C4 | Every presenter ID exists in `people.yml`, and every tag in `tags.yml` (aliases resolved) | error |
| C5 | Demo slugs are unique within a week, so anchors are unique | error |
| C6 | Summary is 10–120 words, title ≤ 80 chars, headline ≤ 200 chars | error |
| C7 | 1–4 tags per demo | error |
| C8 | `publishedAt` ≥ `date`, and not in the future for non-draft weeks | error |
| C9 | `review.sensitive` must be `cleared` if the pipeline flagged the demo | error (blocks merge) |
| C10 | Date is a Friday | warning (holiday weeks are allowed) |
| C11 | A week has at least one demo | error |

### 3.3 Unit tests — every PR (Vitest)
- **Site library:** `formatWeekTitle` (UTC only; guard against the classic timezone off-by-one
  that would turn "September 25" into "September 24"), `slugify` (must match the heading-anchor
  algorithm), `buildSidebar` (year groups newest first, current year expanded), `latestWeek`,
  `feedItems` (sorted, limited, absolute URLs), `toMarkdown` (the `.md` export),
  `normalizeTags` (aliases → canonical).
- **Pipeline:**
  - `youtube.ts`: pagination, quota accounting, retry on 5xx/403-quota, private or deleted videos
    skipped with a warning. Uses recorded fixtures (msw).
  - `transcribe.ts`: VTT/SRT → text, speaker/timestamp stripping, empty transcript handling.
  - `summarize.ts` against a **mock Anthropic client**: parses a valid structured output; a
    `stop_reason: "refusal"` or `"max_tokens"` becomes `needsHumanSummary: true` rather than a
    crash; tags outside the taxonomy are rejected; retries only on retryable errors (429/5xx).
  - `generate.ts`: **golden-file snapshot** of the YAML it writes, stable key order, and
    idempotence (a second run changes nothing; human-edited fields are never overwritten without
    `--force`).

### 3.4 Component tests — every PR
Render components with the Astro Container API and assert on the HTML:
- `DemoSection`: an `<h2 id>` containing the title; a byline showing presenter names and tag chips;
  the summary; the video facade.
- `LiteYouTube`: **no `<iframe>` in the initial markup**; a `<button>` with accessible name
  "Play video: {title}"; a thumbnail `<img>` with `alt`, `width` and `height` (so there's no CLS);
  a `youtube-nocookie.com` URL in `data-` attributes.
- `WeekEntry` (index row): an `id` anchor equal to the date slug (`september-25-2026`), a link to the
  weekly page, and the headline.

### 3.5 Build-output tests — every PR, after `astro build`
Run against `dist/`:
- **Pages:** every non-draft week has `dist/demos/YYYY/YYYYMMDD/index.html`. `/demos/` lists all
  of them newest-first. Each year page lists exactly its own weeks. Draft weeks are absent
  everywhere.
- **RSS** (`/demos/rss.xml`): parses as XML; RSS 2.0 required elements are present; `atom:link
  rel="self"`; N items, newest first; every `<link>` points to an existing weekly page in `dist`;
  `guid` is stable (snapshot); `pubDate` is RFC 822; `content:encoded` lists every demo title.
  Also validated with a feed validator (see 3.9).
- **Sitemap / robots / canonical:** every page is in the sitemap; canonical URLs are absolute with
  a trailing-slash policy applied consistently.
- **Markdown and LLM surfaces:** `/demos/YYYY/YYYYMMDD.md` contains every demo title and video
  URL; `/llms.txt` lists every week; `/llms-full.txt` includes transcripts.
- **OG images:** one per page, 1200×630 PNG, under 300 KB.
- **HTML validity:** `html-validate` over index, a year page and a weekly page.
- **Internal links:** `lychee --offline --include-fragments dist/` finds no broken internal links
  or anchors.

### 3.6 End-to-end — every PR (Playwright; Chromium plus mobile emulation, WebKit nightly)
Against `astro preview`. All `*.youtube*.com`, `*.ytimg.com` and `*.googlevideo.com` requests are
intercepted with `page.route` and stubbed.

| ID | Scenario | Assertions |
|---|---|---|
| E1 | Index loads | H1 "Demos"; Subscribe links to `/demos/rss.xml`; the "latest" callout points to the newest week; entries in date order |
| E2 | Index anchors | Opening `/demos/#september-25-2026` scrolls that entry into view |
| E3 | Weekly page | One H2 per demo; TOC entries = demos; clicking a TOC item updates the URL hash and scrolls |
| E4 | Video facade | **0 requests to YouTube on load**; clicking play inserts one `iframe[src*="youtube-nocookie.com/embed/{id}"]` with `autoplay=1` and a `title` |
| E5 | Keyboard | Tab reaches the play button; Enter activates it; focus moves into the player |
| E6 | Sidebar | Year groups exist, the current year is expanded, and a week link navigates |
| E7 | Search | Searching a known demo title (Pagefind) returns its weekly page |
| E8 | Prev/next | Pagination links go to the adjacent weeks |
| E9 | Theme | The dark mode toggle works and persists across navigation |
| E10 | Mobile (390×844) | Index date labels stack above content; no horizontal scroll |
| E11 | 404 | An unknown week shows the 404 page with a link back to `/demos/` |

### 3.7 Accessibility — every PR
- `@axe-core/playwright` on the index, a year page and `week-huge`, in light **and** dark: **zero
  serious or critical violations** (a merge gate).
- Heading outline: exactly one H1; demos are H2.
- Brand colour contrast checked for text and focus rings in both themes.
- Before launch: a manual screen-reader pass (VoiceOver and NVDA) and a keyboard-only pass.

### 3.8 Performance — every PR (Lighthouse CI)
`lhci autorun --collect.staticDistDir=dist` on `/demos/` and `week-huge`:

| Metric | Budget |
|---|---|
| Performance score | ≥ 0.90 (mobile preset) |
| LCP | ≤ 2.5 s |
| CLS | ≤ 0.05 |
| TBT | ≤ 200 ms |
| Transferred bytes before interaction | ≤ 1 MB, with 0 YouTube requests (backed up by E4) |

This is the test that justifies the lite-embed facade. A page with 34 real YouTube iframes loads
several MB of player JavaScript up front.

### 3.9 Feed and SEO validation
- In CI: a local validator library plus the structural assertions in 3.5.
- Weekly scheduled job: submit the production feed to the W3C Feed Validation Service and fail
  the job on errors.

### 3.10 Visual regression — every PR (non-blocking at first, blocking after launch)
Playwright `toHaveScreenshot` for the index, `week-typical` and a year page × {desktop, mobile} ×
{light, dark}. Runs in the official Playwright Docker image so fonts render the same everywhere.
Baselines are updated only with a `update-snapshots` label and a human review of the diff.

## 4. Pipeline integration tests

| ID | What | When |
|---|---|---|
| P1 | `npm run demo:draft -- --week 2026-01-09 --from-fixtures tests/fixtures/pipeline/…` with a mocked Claude client writes YAML identical to the golden file | every PR |
| P2 | Same run with `--dry-run` writes nothing and prints a diff | every PR |
| P3 | Re-running on an already-edited week keeps human edits | every PR |
| P4 | **Live sandbox run**: real YouTube test playlist (2 short private videos) + real Claude call → PR against a sandbox branch | weekly schedule and on pipeline releases |
| P5 | Quota guard: a simulated quota exhaustion fails with a clear message and a non-zero exit | every PR |

## 5. Editorial checks (the PR review checklist)

The drafting bot's PR template requires a reviewer to tick:
- [ ] Every summary is accurate (watched or skimmed each video)
- [ ] No customer data, credentials, internal URLs or unreleased partner names on screen or in text
      (the pipeline's `sensitive` flags are resolved)
- [ ] Presenters and tags are correct; the headline reads well
- [ ] Videos are set to the intended visibility (unlisted/public)
- [ ] Preview deployment checked on desktop and mobile

CODEOWNERS on `src/content/demos/**` requires one approval from the editorial group.

## 6. LLM evaluation (summariser and tagger)

**Dataset:** 25–30 real internal demo transcripts, each with a human-written reference summary,
reference tags and expected sensitive flags. Add adversarial cases: a transcript containing an
email address or API key, a customer name, a 15-second clip, heavy off-topic chatter, two
presenters, and a mostly non-English transcript.

**Deterministic assertions (must pass 100%):**
- Output matches the JSON schema; tags ⊂ taxonomy (the enum is in the schema); 1–4 tags.
- Summary is within the configured word range; third person; starts with the presenter's first
  name or "Demo of".
- No email addresses, URLs with tokens or key-like strings in any output field.
- `sensitive.flagged === true` for every case whose reference is flagged (recall on this class
  must be 100%).

**Model-graded assertions (tracked, with thresholds):**
- Faithfulness: every claim is supported by the transcript (LLM judge with a rubric) — ≥ 95%.
- Coverage: the main feature shown is named — ≥ 90%.
- Tag agreement with the reference (Jaccard) — ≥ 0.7 on average.

**When:** on PRs that touch `pipeline/prompts/**`, the model ID or the schema; and on a weekly
schedule to catch model drift. Results are posted as a PR comment and compared against the
stored baseline. A drop of more than 5 points fails the check.

**Production signal:** the review PR diff is feedback in itself. Track the *edit rate* (% of
generated summaries a reviewer changed) per week. Rising edit rates mean the prompt needs work.

## 7. Post-deploy and scheduled checks

| Check | When | Pass criteria |
|---|---|---|
| Smoke: `/demos/`, latest week, `/demos/rss.xml`, `/sitemap.xml`, `/llms.txt` | after every production deploy | 200s, correct `content-type`, first RSS item = newest week |
| One Playwright smoke test (E1 + E4) against production | after every production deploy | green |
| External link check (`lychee` with cache and rate limit) | weekly | no new broken links |
| **Video availability**: YouTube oEmbed for every video ID | weekly | a private or deleted video opens an issue naming the week and demo |
| Lighthouse on production | weekly | within budgets |
| W3C feed validation | weekly | valid |

## 8. CI wiring

| Workflow | Trigger | Jobs (in order; each gates the next) |
|---|---|---|
| `ci.yml` | pull_request, push to main | static checks → content validation + unit + component → `astro build` → build-output tests + lychee offline → Playwright E2E + axe (sharded) → Lighthouse CI → visual regression; preview deploy with URL comment |
| `evals.yml` | PR paths `pipeline/prompts/**`, `pipeline/src/summarize.ts`, schedule | promptfoo/Vitest evals → PR comment |
| `draft-week.yml` | schedule (Sat 15:00 UTC) + `workflow_dispatch(week)` | pipeline run → `peter-evans/create-pull-request` |
| `deploy.yml` | push to main | build → deploy → smoke tests → notify |
| `healthcheck.yml` | weekly schedule | external links, video availability, Lighthouse prod, feed validator; opens issues on failure |

Required status checks on `main`: static checks, content validation, unit/component, build, build-output tests,
E2E, axe. Lighthouse and visual regression start as advisory and become required after launch.

## 9. If we choose Mintlify instead

| Layer | Change |
|---|---|
| Content validation | No build-time schema. Validate `.mdx` frontmatter and the week data with our own Vitest script, and test that `docs.json` lists every weekly page |
| Build-output tests | Replace with `mint broken-links` in CI, plus checks against the **preview deployment URL** (feed, `.md`, sitemap) |
| E2E / axe / Lighthouse | Run against the Mintlify preview URL. We can't control the embed markup, so E4 and the performance budget become observations rather than gates |
| Generator tests | More important: the pipeline must edit 4 files per week (week page, index `<Update>` + Callout, year page, `docs.json`), so golden-file tests cover all four |

## 10. If we adopt the TypeSafe option

Build plan section 11 adds a TypeSafe call next to the Claude call. It asks yes/no questions for
tags, sensitive flags and thin transcripts, runs in shadow mode for 4 live weeks, and then we
switch to it or drop it. The other layers (sections 3.1, 3.2 and 3.4–3.10) don't change: the
option writes the same week YAML fields, so C4, C7 and C9 still guard its tags and flags.

**Fixtures (section 2):** recorded TypeSafe responses (a full answer set, a 529 overload, and a
response missing one answer), and a `tags.yml` fixture with descriptions, because the
descriptions become question text.

**Unit tests (section 3.3):** `judge.ts` runs against a stubbed `fetch` (the SDK accepts one), with
retries off (`retry: { maxRetries: 0 }`) so the error cases run instantly.
- The request has one question per tag and the pinned model ID. Answers map back to tag IDs,
  including IDs with hyphens.
- The policy gives 1–4 tags, warns when no tag clears the threshold, flags the demo when any
  reason clears it, and sets `confidence: low` when `explains_feature` is below its threshold.
- The regexes flag an email address, a key-like string or an internal hostname even when every
  answer is 0.
- After a switch, a 529 or a missing answer keeps Claude's tags and marks the demo `flagged`. In
  shadow mode, it only adds a PR note. The SDK returns a partial answer set without an error, so
  `judge.ts` must check that every question was answered.

**Pipeline integration (section 4):** P1 runs in both `judge` modes and also compares the
judgments file with a golden file. P2 writes no judgments file. P4 makes real TypeSafe calls and
fails if the answering `model` isn't the pinned version.

**Editorial checks (section 5):** the PR table shows TypeSafe's probabilities and near-misses, and
the checklist gains one line, so misses can be counted:
- [ ] Anything sensitive that no flag caught is labelled `sensitive-miss`

**LLM evaluation (section 6):** Claude and TypeSafe run on the same golden set.
- **Same gates.** The deterministic assertions on tags and flags apply to TypeSafe's output too:
  tags from the taxonomy, 1–4 per demo, and 100% sensitive recall at the configured threshold.
- **New cases, for both, aimed at literal reading and false alarms:** a password-reset demo that
  never reveals a password, a presenter who says there's no customer data while naming a customer,
  a demo that uses only sandbox names like Acme, and a demo that fits no tag.
- **Threshold sweep.** It replays stored answers, so it needs no new API calls. At each threshold
  it reports sensitive recall, false flags per week and tag Jaccard, and it names the values the
  build plan's rules pick. Thresholds change only in a reviewed PR.
- **Calibration (tracked).** Tag probabilities are grouped into buckets (0–0.1, 0.1–0.2, …), and
  each bucket is compared with how often the reference has that tag.
- **Stability (tracked).** The golden set runs 3 times through TypeSafe, and any tag or flag that
  flips between runs is reported. Claude gets the same check once, before the switch decision,
  so its eval cost doesn't triple every week.
- **Failure triage.** Each failed case is reported with its state, questions, answers and the
  policy's decision. It's classed as missing evidence (for example, data that was only on screen),
  a model error, a policy or code error, or a service failure (with its request ID). Misses classed
  as missing evidence don't count against either judge in the switch decision; closing that gap
  is the Phase 6 frame check's job.

**Shadow weeks and the switch (build plan section 11.2):** the weekly `evals.yml` run also scores
the newest merged week. It compares each judge's tags with the editor's final tags (Jaccard), and
counts sensitive misses (anything the editor or Claude caught that TypeSafe didn't, including
`sensitive-miss` labels), false flags and fallbacks. Results go to one tracking issue. After 4
weeks, these numbers and the golden set decide the switch. After a switch the weekly scoring
continues, and a rising fallback count opens an issue, as the healthcheck does.

**CI wiring (section 8):** `evals.yml` also runs when `pipeline/src/judge.ts`, the thresholds, the
pinned Jev version or `src/data/tags.yml` change, because tag descriptions are question text.
`TYPESAFE_API_KEY` goes to `evals.yml`, `draft-week.yml` and the P4 job, never to `ci.yml`.
