# How docs.omni.co/demos works — teardown

> Research date: 2026-09-28. Every number below comes from the live site and can be regenerated
> with [`research/omni_demos_stats.py`](../research/omni_demos_stats.py).

## TL;DR

- **What it is:** a *weekly video changelog*. Every Friday Omni's engineers record short demos
  (one video per feature). A few days later each batch is published as one docs page
  (`/demos/2026/20260925`) with a title, a *presenter · tags* byline, a one-paragraph summary and a
  YouTube embed for every demo. An index page (`/demos`) lists every week and produces an RSS feed.
- **How it's built:** plain MDX in a [Mintlify](https://mintlify.com) docs site. The source repo,
  `exploreomni/mintlify-omni`, is private; the site's CSS references it. The pages use stock
  Mintlify pieces: the `<Update>` changelog component (which produces the RSS feed), `<Callout>`,
  `<Tip>`, `<Note>` and `<Frame>` around a YouTube `<iframe>`. There's no custom video tooling on
  the page. Videos are **public** uploads on the *Omni Analytics* YouTube channel, titled
  `YYYY-MM-DD <Demo title>`, and the YouTube description is identical to the docs summary.
- **Scale:** 150 weekly pages (Oct 20 2023 → Sep 25 2026), **1,787 videos** (100% YouTube) from
  **125 different presenters**. Videos per week grew from a median of 7 (2023) to 17 (2026),
  peaking at 34.
- **Why it works:** the pages are cheap to produce (MDX plus YouTube links), anyone can subscribe
  (RSS, which feeds Slack), and it's discoverable (in the docs search, sitemap, `llms.txt` and
  per-page `.md` exports).
- **Weaknesses we can fix:** one week has to be edited in 4 places, and tags are free text (145
  spellings of 116 tags, and since March 2026 no delimiters at all). The RSS feed links to index
  anchors and only has 15 items. There are no transcripts, no per-demo pages and no filtering,
  up to 34 full YouTube players sit on one page, and old permalinks were lost in two platform
  moves.

---

## 1. What the "Demos" product is

There are two layers:

1. **A program:** a weekly internal demo session on Friday (144 of 150 weeks are dated on a
   Friday; 5 of the 6 exceptions are US holiday weeks). Engineers, designers and solutions
   engineers show what they built or are experimenting with. Omni's CEO describes it as "we demo
   product every single week… Every week, we cut up like 10 of things that we're working on"
   ([podcast, Apr 2025](https://www.buzzsprout.com/1940011/episodes/16978622-what-it-takes-to-build-a-bi-platform-colin-zima-ceo-of-omni)).
   A co-founder mentioned "our Friday demos" in Oct 2023
   ([LinkedIn](https://www.linkedin.com/posts/jamescdavidson_october-6-2023-demos-omni-analytics-activity-7117539298165362688-Iz8i)).
   Every demo is published as its **own short video**; there has never been one long recording
   with timestamps.
2. **A publication:** the clips are uploaded to YouTube and published on the docs site, usually
   **1–4 days after demo day** (median 1.9 days, based on RSS `pubDate`s).

Weekly pages carry a disclaimer that sets expectations:

> Demos highlight what we are working on or experimenting with, but are not a guarantee of
> release. Let us know your thoughts at support@omni.co.

The "Product updates" tab also has a separate **Changelog** (text release notes: "New features,
improvements, and bug fixes"). Demos show *work in progress*; the changelog records *what shipped*.

## 2. Information architecture

```
docs.omni.co
└── Tab: "Product updates"
    ├── Menu item: "Demos"  (icon: rocket, "Weekly updates of upcoming and experimental features")
    │   ├── /demos                     "All demos"  ← index: every week as an <Update>, rss: true
    │   ├── Group "2026" (expanded)    root: /demos/2026  ← year archive (bulleted list)
    │   │   ├── /demos/2026/20260925   "September 25, 2026"
    │   │   ├── /demos/2026/20260918   …
    │   ├── Group "2025" (collapsed)   root: /demos/2025
    │   ├── Group "2024" (collapsed)   root: /demos/2024
    │   └── Group "2023" (collapsed)   root: /demos/2023
    └── Menu item: "Changelog"         /changelog
```

- **URL scheme:** `/demos/{YYYY}/{YYYYMMDD}`. The file path matches the URL
  (`demos/2026/20260925.mdx`).
- **Sidebar:** every weekly page is listed by hand under its year group in `docs.json`. Sidebar
  titles are the dates. The current year is expanded and past years are collapsed.
- **Search:** all demo pages are in the site search. Search filters by section ("Product updates"
  155 pages, "Demos" 151 pages).

## 3. Page anatomy

### 3.1 Index page — `/demos` (`demos/index.mdx`)

Frontmatter (recovered from the page's hydration data):

```yaml
title: Omni Demos
sidebarTitle: All demos
description: Watch weekly video demos of new and upcoming Omni features, including AI, dashboards, modeling, embedding, and platform updates.
mode: center      # centred layout: no table of contents, no tag filters
rss: true         # Mintlify generates /demos/rss.xml from the <Update> blocks below
```

Body (abridged; this is the real markdown export at `https://docs.omni.co/demos.md`):

```mdx
<Tip>
  **Want to be notified about new updates?** Click the **Subscribe** button and use the URL to set up
  an RSS feed in [Slack](https://slack.com/help/articles/218688467-Add-RSS-feeds-to-Slack) or an
  [RSS aggregator](https://feeder.co/).
</Tip>

<Callout icon="circle-play" color="#FF5FA2" iconType="regular">
  **Check out the latest demo!**

  [September 25, 2026](/demos/2026/20260925): Single-Content Users, Drill Down in Apps, …
</Callout>

<Update label="September 25, 2026" rss={{title: "September 25, 2026", description: "Single-Content Users, Drill Down in Apps, …"}}>
  [September 25, 2026](https://docs.omni.co/demos/2026/20260925): Single-Content Users, Drill Down in Apps, …
</Update>

<Update label="September 18, 2026" rss={{…}}>
  …
</Update>
<!-- … 150 <Update> entries in total, newest first, back to October 20, 2023 -->
```

How it renders:
- Each `<Update>` is a **two-column row**: a sticky 160px column on the left with the date label
  and a hover anchor (`#september-25-2026`), and the content on the right. On mobile the columns
  stack.
- Mintlify adds an RSS button (`data-testid="rss-feed-button"`) to `rss: true` pages. Omni's
  custom CSS turns it into a pink pill labelled **"Subscribe"**
  (`[data-testid="rss-feed-button"]::after { content: "Subscribe" }`).
- The "latest demo" `<Callout>` is **maintained by hand**. It repeats the newest entry.

### 3.2 Year archive — `/demos/2024` (`demos/2024/index.mdx`)

A `<Note>` pointing to the RSS feed, then a hand-written bulleted list:
`* [December 20, 2024](/demos/2024/20241220): Controls in Tiles, Topic-less AI, …`

### 3.3 Weekly page — `/demos/2026/20260925`

Frontmatter is just `title` (the date) and `description` (the headline list of topics). Body:

```mdx
<Note>
  **Stay in the loop!** Subscribe to the [demo RSS feed](/demos/rss.xml) to be notified when we post new demos.

  Demos highlight what we are working on or experimenting with, but are not a guarantee of release. …
</Note>

## CI Dashboard

*`Luke Bowerman · Internal Developer Productivity`*

Luke demos a new CI dashboard showing continuous integration run volume and performance gains — CI run
times dropped from ~36 minutes to ~24 minutes (30% faster) while costing 2% less. …

<Frame>
  <iframe src="https://www.youtube.com/embed/7xPUiKpDylQ" width="100%" height="400"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
</Frame>

## External (Single Content) Users
…  (17 sections this week; median 17 per week in 2026, max 34)
```

Observations:
- **Every demo is an H2**, so each one gets an anchor (`#ci-dashboard`) and a right-hand
  table-of-contents entry. That TOC is the week's "menu".
- **Byline** = presenter · tags. Every week since the first has one, but the format has changed
  four times:

  | Period | Markdown | Note |
  |---|---|---|
  | 2023-10 → 2024-07 | ``*Richard Czechowski · `calcs` `table` `workbook`*`` | lowercase tag slugs, one code span each |
  | 2024-07 → 2024-08 | ``*`Dashboards` `Filters`*`` | tags only, no presenter |
  | 2024-09 → 2026-02 | ``*Chris Merrick · `Ai` `Modeling`*`` | Title Case tags |
  | 2026-03 → now | ``*`Trip Tate · Ai Dashboards`*`` | whole byline in one code span: **tags no longer delimited** |

  There's **no controlled vocabulary**. Across the archive, 145 tag spellings reduce to 116 tags
  after case-folding. There are 29 case-variant pairs ("Workbook"/"workbook"), singular/plural
  duplicates ("dashboard"/"dashboards") and typos ("adminstration"). Since March 2026, multi-word
  tags can't be told apart ("Maps Visualization Apps").
- **Summaries** are short: a median of **25–27 words** per demo in every year (p90 ≈ 45). The
  latest week runs longer (median 50 words). The voice changed abruptly on **2026-05-01**:
  - Up to April 2026: chatty, first person ("Bring the vibes.").
  - Since May 2026: uniformly neutral third person with em-dashes ("Luke demos …"), plus asides
    like *"Note: customer environment likely visible on screen."*

  That strongly suggests summaries are now generated by an LLM from the recording, then lightly
  edited.
- **Embeds:** plain `https://www.youtube.com/embed/{id}` with no query parameters, no
  `youtube-nocookie.com`, no `title` attribute (an accessibility gap) and no click-to-load
  facade. The iframes aren't in the server-rendered HTML; Mintlify renders them on the client.
  We couldn't measure from this environment whether it lazy-loads them.
- The only components used on weekly pages are `<Frame>` (1,787 uses) and `<Note>` (151).

## 4. Machine-readable surfaces (all generated by Mintlify)

| Surface | URL | Notes |
|---|---|---|
| RSS 2.0 | `/demos/rss.xml` | Built from the index's `<Update>` blocks (`rss: true`). **Only the latest 15 items.** `<title>` = label, `<description>` = the `rss` prop, `<link>` = **index anchor** (`/demos#september-25-2026`), `<guid isPermaLink="false">` = hash, `<pubDate>` = when the entry first appeared, `content:encoded` = the entry's rendered HTML. |
| Markdown export | `/demos/2026/20260925.md` | Every page. Advertised with `<link rel="alternate" type="text/markdown">`. |
| LLM index | `/llms.txt`, `/llms-full.txt` | Full docs corpus (≈5 MB). In `llms-full.txt` the iframe attributes are stripped (`<iframe />`). |
| Sitemap | `/sitemap.xml` | 155 demo URLs (index + 4 year pages + 150 weeks) out of 1,203. |
| Social cards | `/_mintlify/api/og?division=2026&title=…&description=…` | OG/Twitter images (1200×630) generated per page. `division` = the nav group (year). |
| SEO | canonical, `og:*`, `twitter:*`, meta description = page `description` | |

## 5. The platform (Mintlify configuration in use)

From the `docsConfig` embedded in the page:

- `theme: "aspen"`, brand colour `#FF5FA2`, heading font Cal Sans, body font IBM Plex Sans,
  custom light/dark background colours, light and dark logos.
- Navbar: "Community" link plus a primary CTA button "Try Omni!". A dismissible site banner.
- `integrations.ga4` (Google Analytics 4).
- Built-in features Omni relies on: full-text search with section filters, **AI assistant**
  ("Ask AI"), page feedback (thumbs up/down), light/dark toggle, prev/next pagination, contextual
  page menu, auto-generated OG images.
- **Custom CSS** (the Subscribe pill, heading typography, side-by-side layouts, guide page layout)
  and some custom React (`GuideSidebar`) in the repo.

## 6. By the numbers

| Year | Weeks | Videos | Median videos / week | Min | Max | Distinct presenters |
|---|---:|---:|---:|---:|---:|---:|
| 2023 (from Oct 20) | 9 | 58 | 7 | 2 | 9 | 18 |
| 2024 | 51 | 407 | 8 | 2 | 14 | 32 |
| 2025 | 51 | 638 | 12 | 6 | 22 | 70 |
| 2026 (to Sep 25) | 39 | 684 | 17 | 5 | 34 | 88 |
| **Total** | **150** | **1,787** | | | | **125** |

- 1,785 unique YouTube IDs across 1,787 embeds. 100% `youtube.com/embed`.
- 1,764 bylines. Tags: 145 spellings, 116 after case-folding, 29 case-variant groups; 498 bylines
  (all of them since March 2026) have tags run together with no delimiter.
- Summary length per demo: median 24 (2023), 25 (2024), 27 (2025), 27 (2026) words.
- YouTube: the videos are public on the channel (@omni_analytics) and get low view counts (e.g.
  35 views on a recent demo). The docs page, not YouTube, is the main distribution channel. A
  public playlist, "Weekly Engineering Development Demos", has 812 videos but looks stale.
- Demo day: Friday 144×, Monday 4×, Thursday 2× (holiday weeks).
- RSS publish lag after demo day: 1.1–3.8 days (median 1.9).
- Weekly page HTML ≈ 420 KB. Index page HTML ≈ 755 KB, because all 150 entries sit on one page.

## 7. The publishing workflow (inferred from public evidence)

The docs repo is private, so this is reconstructed from timestamps and page content.

1. **Friday:** the demo session. It's likely a live meeting that is then cut into one clip per
   demo. At least some clips are recorded in Loom: two demos on 2026-03-20 link to
   `loom.com/share/…` instead of YouTube.
2. **Upload:** each clip goes to the *Omni Analytics* YouTube channel, titled
   `YYYY-MM-DD <Demo title>` (the date prefix is the demo date).
3. **Publish, and it looks scripted:**
   - All 14 videos for the 2026-09-25 week went **public within a 9-second window** on Saturday
     09-26.
   - The 15th went public on Monday 09-28 at 14:41:26, **8 seconds before** the docs RSS `pubDate`
     (14:41:34).
   - Every YouTube description is **identical** to its docs summary.

   Together these point to one tool that (a) makes the week's videos public, (b) writes their
   descriptions and (c) generates and merges the docs change from a single source of truth.
4. **The docs change** (whether a script or a person makes it) touches **4 files**:
   - adds `demos/2026/YYYYMMDD.mdx` (title, headline description, the Note, then one H2 section
     per demo with byline, summary and `<Frame><iframe>`),
   - adds an `<Update>` to `demos/index.mdx` and **rewrites the "latest demo" `<Callout>`**,
   - adds a bullet to `demos/2026/index.mdx`,
   - adds the page to the 2026 group in `docs.json`.
5. **On deploy:** Mintlify picks up the new `<Update>`; its RSS `pubDate` is the deploy time.
   Readers who subscribed via Slack or an RSS reader get notified. RSS is the only notification
   channel; Omni's newsletter is quarterly.

The only public trace of Omni's docs automation is a workflow in their open-source CLI repo
(`exploreomni/cli/.github/workflows/notify-docs.yml`). It uses `peter-evans/repository-dispatch`
to send a `generate-docs` event to the docs repo on release. That covers reference docs, not
demos, but it shows the pattern: **automation in other repos triggers doc generation in the docs
repo.**

**History worth learning from:**
- Oct 2023: the demos lived at `docs.exploreomni.com/demos/2023/10/06/` (blog-style paths).
- 2024 → early 2026: weekly pages also existed at `omni.co/demos/YYYYMMDD`. Those now
  **301-redirect to the index, not to the matching week**, so old deep links lose their target.
- Weeks before 2023-10-20 now return 404.

**Permalinks and redirects need to be designed in from day one.**

**The separate text changelog** (`/changelog`, with its own `/changelog/rss.xml`) uses
`<Update label="Week of September 14, 2026">` entries dated by Monday. They are grouped under
bold area headings (AI, API, Modeling, …) and list what shipped, deprecations and bug fixes, with
links into the docs. Demos are previews with a "not a guarantee of release" disclaimer; the
changelog records what actually shipped. Some 2024 changelog entries link to demo pages.

## 8. Lessons for our build

| Omni today | What we'll do instead |
|---|---|
| One new week means edits in **4 places** (week page, index `<Update>` + Callout, year page, `docs.json`) | **One source of truth per week** (a data file). Index, year archives, sidebar, "latest" callout and feeds are all *generated* from it. |
| Byline tags are free text (145 spellings of 116 tags; undelimited since 2026-03) | A **controlled tag taxonomy** (`tags.yml` with aliases), enforced by schema validation in CI. |
| Old permalinks 301 to the index, and pre-Oct-2023 weeks are gone | **Stable permalinks** (`/demos/YYYY/YYYYMMDD/`) and a redirect map that's tested in CI. Nothing ever gets deleted without a redirect. |
| YouTube description and docs summary are kept in sync by a private tool | The **week data file is the source of truth**; after merge, a publish step sets the videos Public and writes their descriptions from it (Phase 4). |
| Presenters are free-text names | A **people registry** (`people.yml`): name, team, avatar. Enables presenter pages later. |
| RSS: last 15 items only, links to index anchors | RSS (Atom/JSON Feed optional) with a **configurable item count**, each linking to the **weekly page**, and a stable `guid` per week. |
| Summaries only | Also store the **transcript** (collapsible, searchable, and included in `llms-full.txt`). Captions help accessibility too. |
| Up to 34 full YouTube players per page | A **lite YouTube facade** (thumbnail + play button; the iframe loads on click) on `youtube-nocookie.com`, with a `title` on every iframe. |
| No per-demo URL beyond `#anchor` | Anchors stay. Optional per-demo pages and **tag/presenter filters** later. |
| Human writes the whole page | A **pipeline drafts the page** (ingest → transcribe → summarise with Claude → open a PR). A human reviews, edits and merges. |
| Customer data can appear on screen ("customer environment likely visible") | Videos stay **Unlisted until review**, the summariser outputs a **sensitive-content flag**, and a reviewer checkbox is required before merge. |

## Appendix: reproduce these numbers

```bash
python3 research/omni_demos_stats.py --cache-dir .cache/omni --json omni_stats.json
```

The script downloads the sitemap, the `.md` export of all weekly pages and the RSS feed (about 20
seconds, standard library only), and prints the per-year table above.

## Sources

- Live site: https://docs.omni.co/demos, https://docs.omni.co/demos.md,
  https://docs.omni.co/demos/rss.xml, https://docs.omni.co/sitemap.xml,
  https://docs.omni.co/llms.txt, https://docs.omni.co/llms-full.txt, the 150 weekly
  `/demos/YYYY/YYYYMMDD.md` exports, and https://docs.omni.co/changelog.md.
- Mintlify changelog docs (the `<Update>` component, `rss: true`, tags):
  https://mintlify.com/docs/create/changelogs
- YouTube oEmbed for 7xPUiKpDylQ / dwqbK_XibYI, channel @omni_analytics, playlist
  PLF3lBuvvkZtIcDmGWThuyvNq_3vqUTxDd, and the channel uploads feed
  (https://www.youtube.com/feeds/videos.xml?channel_id=UC1y1XIm2RcLVhm_TtoxkpTQ).
- GitHub: https://github.com/exploreomni/mintlify-omni (404, private),
  https://raw.githubusercontent.com/exploreomni/cli/main/.github/workflows/notify-docs.yml
- Program: LinkedIn posts by Omni's co-founders (linked in section 1), the Buzzsprout podcast
  (linked in section 1), https://www.iconiq.com/growth/insights/backing-omni-redefining-business-intelligence
