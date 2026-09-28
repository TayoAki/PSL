# Open-source landscape

> Research date: 2026-09-28. Star counts and versions are as shown on GitHub or npm that day.
> Sources are listed at the end of each section.

## TL;DR

- **No open-source project replicates the Omni demos hub as a product.** We found no "demo day"
  or video-changelog app worth forking. The closest reusable things are:
  1. docs frameworks that can produce dated entries with an RSS feed,
  2. public changelog sites we can study, and
  3. mature tools for each pipeline stage (transcription, embeds, feeds, CI).
- **Recommended stack: Astro Starlight** (MIT). It is static, has Pagefind search built in, and
  validates content with Zod. Cloudflare runs a large changelog with RSS on it. We confirmed
  the architecture with a spike (section 5).
- **Runners-up:**
  - **Fumadocs** (Next.js): the closest to Mintlify's AI and LLM features.
  - **Docusaurus**: the most complete built-in blog feed, with authors and tags enforced.
- **Buy option: Mintlify** (what Omni uses). The free Starter plan covers most of what the demos
  hub needs. The AI assistant needs Pro at $450/month. The renderer isn't open source, and
  self-hosting is Enterprise-only.

## 1. Docs frameworks

Every option below has dark mode and callout components built in.

| Stack | License · stars · activity | Dated entries + RSS | YouTube embed | Search | llms.txt / `.md` per page | Content schema | AI chat |
|---|---|---|---|---|---|---|---|
| **Astro Starlight** | MIT · 9.3k · v0.42.4 (Astro 7), daily commits | `@astrojs/rss` over any collection; `starlight-blog` plugin (RSS, tags, authors) | `astro-embed` `<YouTube>` = lite-youtube-embed facade | **Pagefind built in** | `starlight-llms-txt` (docs collection only); `.md` via small community plugin or own endpoint | **Zod** (fails the build) | Third-party only |
| **Fumadocs** (Next.js) | MIT · 13.2k · v16, daily commits | Collection + `feed` package (official guide) | none built in | Orama built in | **Built in**: llms.txt/-full, `.md` URLs, "Copy Markdown / Open in ChatGPT" | Zod / Standard Schema | **Built-in** Ask-AI UI (your own model key) |
| **Docusaurus** | MIT · 66.4k · 3.10.2 | **Best built in**: blog plugin with RSS/Atom/JSON, several instances, `authors.yml`, `tags.yml` + `onInlineTags: 'throw'` | add react-lite-youtube-embed | Algolia DocSearch or local plugin | `docusaurus-plugin-llms` | Built-in keys only | DocSearch Ask AI (bring a key) |
| Nextra 4 | MIT · 13.9k · commits slowing (last 2026-06-23) | Blog theme RSS recipe | none | Pagefind | "Copy page" only | none | via Inkeep |
| VitePress | MIT · 18.4k · 1.6.4 (2.0 still alpha) | DIY via `createContentLoader` | none | MiniSearch / Algolia | `vitepress-plugin-llms` | none | none |
| MkDocs Material | MIT · 27.5k · **maintenance mode since Nov 2025** | blog + `mkdocs-rss-plugin` | none | built in | `mkdocs-llmstxt` | none | none |
| Zensical (MkDocs successor) | MIT · 5.8k · v0.0.66, pre-1.0 | native blog + RSS (Sep 2026) | none | built in | unverified | none | none |
| Rspress | MIT · 2.3k · v2, daily commits | `@rspress/plugin-rss` | none | built in | **Built in** (SSG-MD) | none | none |
| Docus (Nuxt) | MIT · 3.1k · v5.13 | DIY server route | Nuxt Scripts YouTube facade | built in | **Built in** + MCP server | Zod (Nuxt Content) | **Built in** (needs a server) |

### Mintlify (the "buy" option Omni uses)
- **Licence:** the `mint` CLI (npm, v4.2.946) is **Elastic-2.0**, which is source-available, not
  OSI open source. The renderer repo is no longer public. The `starter`, `docs` and
  `components` repos are MIT.
- **Self-hosting:** Enterprise plan only, set up with their team (AWS CDK or a Helm chart).
- **Free Starter plan:** 5 editors, custom domain, search, MCP and Git sync. No AI assistant.
- **Pro plan:** $450/month on annual billing. It adds the AI assistant, with 10k AI credits a
  month (about 400 answers).
- **Changelog RSS:** `<Update>` plus `rss: true` produces `{page}/rss.xml`. It works on public
  docs only. We saw it cap at 15 items, with each item linking to an anchor on the index.

### Ranking for our use case
Criteria: parity with Omni's pages, low maintenance, easy weekly PRs for non-engineers, and
testability in CI.

1. **Astro Starlight.**
   - Static output with nothing to run.
   - Zod turns content mistakes into build failures.
   - The lite YouTube facade matters with 10–34 videos per page.
   - Pagefind, sitemap and dark mode are built in.
   - Gaps: an AI chat needs a third-party service or our own endpoint. `llms.txt` and `.md`
     exports are best written as our own endpoints (about 50 lines each), because
     `starlight-llms-txt` ignores data-driven pages.
2. **Fumadocs.** The best AI and LLM features out of the box. The cost is owning a Next.js app,
   writing RSS ourselves, and running a server for the chat.
3. **Docusaurus.** The most complete dated feed with no custom code: presenters and tags in YAML
   that fail the build if unknown, and `onBrokenLinks: 'throw'`. Gaps: a YouTube facade and AI
   need add-ons, and custom frontmatter isn't validated.

Avoid for now:
- MkDocs Material: it is at end of life.
- Nextra: activity is slowing.
- VitePress: 2.0 has stayed in alpha.
- Docus: worth a look only if we're a Vue shop.

Sources: https://github.com/withastro/starlight · https://starlight.astro.build/guides/pages/ ·
https://starlight.astro.build/guides/site-search/ · https://docs.astro.build/en/guides/content-collections/ ·
https://github.com/HiDeoo/starlight-blog · https://github.com/delucis/starlight-llms-txt ·
https://astro-embed.netlify.app/components/youtube/ · https://github.com/fuma-nama/fumadocs ·
https://fumadocs.dev/docs/integrations/llms · https://www.fumadocs.dev/docs/guides/rss ·
https://docusaurus.io/docs/blog · https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-content-blog ·
https://github.com/shuding/nextra · https://github.com/vuejs/vitepress · https://squidfunk.github.io/mkdocs-material/blog/ ·
https://github.com/zensical/zensical/releases · https://rspress.rs/guide/basic/ssg-md · https://docus.dev/en/ai/assistant ·
https://registry.npmjs.org/mint/latest · https://www.mintlify.com/docs/deploy/self-host · https://mintlify.com/pricing ·
https://www.mintlify.com/docs/create/changelogs

## 2. Reference implementations to study

| Project | What's reusable | Licence |
|---|---|---|
| **Cloudflare docs** (`cloudflare/cloudflare-docs`, 5.3k) | **The best blueprint.** A Starlight changelog: entries in `src/content/changelog/<product>/*.mdx`, RSS routes in `src/pages/changelog/rss/`, product filters, and a page per entry | code MIT, content CC-BY-4.0 |
| **Supabase www** (`apps/www/pages/changelog.tsx`) | Tag and type filters, **RSS per tag**, a `/changelog.md` export and an "LLM markdown" button (the entries themselves come from a private repo) | Apache-2.0 |
| **GitLab "What's New"** (`data/whats_new/*.yml`) | A schema to borrow from for YAML entries: `name, description, stage, available_in, documentation_link, published_at, release` | MIT |
| OpenStatus (Next.js, MDX changelog) | Per-entry pages. Study only | AGPL-3.0 |
| Openchangelog (Go) | Renders Markdown from Git with RSS, search and tags. Little recent activity | AGPL-3.0 |
| changes-page (Next.js + Supabase) | Database-backed changelog product with widget and email. Not PR-based | AGPL-3.0 |

**Not reusable:**
- posthog.com: its licence forbids copying the site; only `/contents` is MIT.
- Dub: no public changelog.
- Unkey: content is CC BY-NC-ND.
- Cal.com: now closed source.
- Tailwind Plus "Commit": commercial licence.

**No open-source "demo day" or video-library site** turned up that was worth forking.

**Letting non-engineers edit through PRs** (optional, Phase 6):
- Keystatic (MIT, 2.4k; GitHub mode opens a branch and PR)
- Decap CMS (editorial workflow, one PR per entry)
- Pages CMS (MIT)

Sources: https://github.com/cloudflare/cloudflare-docs · https://developers.cloudflare.com/changelog/ ·
https://github.com/supabase/supabase/blob/master/apps/www/pages/changelog.tsx ·
https://gitlab.com/gitlab-org/gitlab/-/raw/master/data/whats_new/202609170001_19_04.yml ·
https://github.com/openstatusHQ/openstatus · https://github.com/JonasHiltl/openchangelog · https://github.com/techulus/changes-page ·
https://github.com/PostHog/posthog.com/blob/master/LICENSE · https://keystatic.com/docs/github-mode · https://decapcms.org/docs/editorial-workflows/ ·
https://pagescms.org/

## 3. Pipeline tooling, stage by stage

| Stage | Pick | Alternatives | Gotchas |
|---|---|---|---|
| **Record** | Whatever presenters already use (Loom, Zoom, OBS). Open-source option: **Cap** (AGPLv3), whose Instant Mode uploads to our own S3/R2 bucket | OBS (GPLv2+, local only, scriptable through obs-websocket); Screenity (GPLv3; share links need paid Pro) | None of these upload to YouTube. AGPL obligations apply if we modify and host Cap's server |
| **Host** | **YouTube** (free; what Omni uses). Presenters upload in YouTube Studio as **Unlisted**; the pipeline only *reads* | Cloudflare Stream (≈ $5–15/month here; free encoding and Whisper captions); Mux (pay-as-you-go includes $20/month credit; auto-captions); Bunny Stream; Vimeo; PeerTube (self-hosted, AGPL) | Uploads through the Data API from an **unverified** project (created after 28 Jul 2020) are forced private until a ToS audit. Quota: `videos.list` and `playlistItems.list` cost 1 unit (10k/day default). Since 2026-06-01 `videos.insert` has its own bucket (100/day). Listing *unlisted* videos needs OAuth as the channel owner |
| **Metadata** | Data API `videos.list` (title, description, duration, date); keyless **oEmbed** for existence checks | yt-dlp (Unlicense) `--skip-download --write-info-json` | YouTube blocks most cloud/CI IPs for scraping ("Sign in to confirm you're not a bot"), which makes yt-dlp and youtube-transcript-api unreliable in GitHub Actions |
| **Transcribe** | **faster-whisper** (MIT). Up to 4× faster than openai/whisper at the same accuracy; int8 on CPU; VAD; word timestamps. Transcribe the **source file** we already have | WhisperX (BSD-2; diarization needs a Hugging Face token); whisper.cpp (MIT); openai/whisper; or **free captions from Cloudflare Stream or Mux** if we host there | `captions.download` costs 200 units and needs edit rights on the video. GitHub runners: 4 vCPU/16 GB (public repos), 2 vCPU/8 GB (private) |
| **Summarise + tag** | **Claude API structured outputs**: `messages.parse()` with a Zod schema. Tags are a JSON-schema **enum** built from `tags.yml` | Borrow prompt ideas (not plumbing) from Fabric's `youtube_summary` / `create_video_chapters` patterns (MIT) | Length limits (`minLength`, `maxLength`) aren't enforced server-side; the SDK validates them client-side. Check `stop_reason` for `refusal` or `max_tokens` before trusting output |
| **Evaluate** | **promptfoo** (MIT; OpenAI announced in 2026-03 that it will acquire it, and it stays open source): `is-json`, `llm-rubric`, `factuality`, `context-faithfulness` in CI | DeepEval `SummarizationMetric`; or plain Vitest assertions plus an LLM judge | Keep the golden set in-repo; run on prompt or model changes and weekly |
| **Embed** | **`@astro-community/astro-embed-youtube`** (MIT). Wraps lite-youtube-embed: thumbnail plus button, iframe loaded on click | paulirish/lite-youtube-embed (Apache-2.0; ~224× faster than the default embed); @justinribeiro/lite-youtube (MIT); react-lite-youtube-embed | Give each embed an accessible label. `youtube-nocookie.com` reduces tracking but Google doesn't promise it is cookie-free, so it doesn't replace consent |
| **Feeds** | **`@astrojs/rss`** (needs `site`; `content` is HTML we build ourselves) | `feed` (MIT) for RSS, Atom and JSON Feed together | Validation: the W3C SOAP API (throttle to ≥ 1 s between calls) or self-hosted `w3c/feedvalidator`. The npm `feed-validator` package is archived |
| **Search** | **Pagefind** (MIT; built into Starlight) | Algolia DocSearch, Orama | Runs after the build; there's no server |
| **LLM surfaces** | Our own endpoints for `/llms.txt`, `/llms-full.txt` and `/demos/…/*.md` | `starlight-page-actions` | llms.txt is an informal proposal; v2 is dated 2026-08-10. Include transcripts in `llms-full.txt` |
| **Automate** | GitHub Actions `schedule` plus `workflow_dispatch`; **peter-evans/create-pull-request@v8** | Keystatic for manual entries | Cron is UTC, runs only on the default branch, can be delayed at the top of the hour, and is **disabled after 60 days of inactivity on public repos**. PRs opened with `GITHUB_TOKEN` **don't trigger CI**, so use a GitHub App token |
| **Test** | Playwright (+ `toHaveScreenshot` in one Docker image), @axe-core/playwright, Lighthouse CI, lychee-action | pa11y-ci; Vale (MDX support since v3.18) for prose | axe finds roughly 57% of WCAG issues automatically, so do a manual pass before launch |

Sources: https://github.com/CapSoftware/Cap · https://github.com/obsproject/obs-studio · https://github.com/alyssaxuu/screenity ·
https://developers.google.com/youtube/v3/determine_quota_cost · https://developers.google.com/youtube/v3/getting-started ·
https://developers.google.com/youtube/v3/revision_history · https://developers.google.com/youtube/v3/docs/videos/insert ·
https://developers.google.com/youtube/v3/docs/captions/download · https://developers.cloudflare.com/stream/pricing/ ·
https://www.mux.com/pricing · https://bunny.net/pricing/stream/ · https://joinpeertube.org/news/release-6.2 ·
https://github.com/yt-dlp/yt-dlp · https://github.com/jdepoix/youtube-transcript-api · https://github.com/SYSTRAN/faster-whisper ·
https://github.com/m-bain/whisperX · https://github.com/ggml-org/whisper.cpp ·
https://docs.github.com/en/actions/reference/runners/github-hosted-runners ·
https://platform.claude.com/docs/en/build-with-claude/structured-outputs · https://platform.claude.com/docs/en/about-claude/pricing ·
https://github.com/danielmiessler/Fabric · https://www.promptfoo.dev/docs/configuration/expected-outputs/ ·
https://openai.com/index/openai-to-acquire-promptfoo/ · https://deepeval.com/docs/metrics-summarization ·
https://github.com/paulirish/lite-youtube-embed · https://github.com/justinribeiro/lite-youtube ·
https://support.google.com/youtube/answer/171780 · https://docs.astro.build/en/recipes/rss/ · https://github.com/jpmonette/feed ·
https://validator.w3.org/feed/docs/soap.html · https://github.com/w3c/feedvalidator · https://pagefind.app/docs/ · https://llmstxt.org/ ·
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows ·
https://github.com/peter-evans/create-pull-request · https://github.com/lycheeverse/lychee-action ·
https://playwright.dev/docs/test-snapshots · https://playwright.dev/docs/accessibility-testing · https://github.com/dequelabs/axe-core ·
https://github.com/GoogleChrome/lighthouse-ci · https://docs.vale.sh/formats/mdx

## 4. What we couldn't verify

- Mintlify: the Pro price reads garbled on the official page; $450 comes from third-party
  write-ups. Which plans include `llms.txt` and `.md` export isn't stated.
- Whether the YouTube Data API can download *auto-generated* captions for our own videos. The
  plan avoids depending on it by transcribing the source file.
- faster-whisper speed on GitHub's 2-vCPU private runners. It's an estimate until Phase 3
  measures it.
- Whether `videos.update` (switching unlisted to public) is restricted for unverified API
  projects. Phase 0 checks this; if it is, an editor flips visibility in YouTube Studio.

## 5. Spike: the recommended architecture, verified

Before recommending Starlight, we built a throwaway spike ([`research/spike-starlight/`](../research/spike-starlight/))
on astro 7.3.5 and @astrojs/starlight 0.42.4. It confirmed:

- **Data-driven weekly pages:** YAML files, via the `glob()` loader, render through
  `<StarlightPage>`.
- **Table of contents:** the right-hand TOC comes from the `headings` prop.
- **Sidebar:** built from the data, with the current year expanded and older years collapsed.
- **Search:** Pagefind indexes the custom pages.
- **RSS:** items link to the weekly page, with the permalink as `guid`.
- **Bad data fails the build:** a malformed video ID or an unknown presenter reference produces
  a precise error.
- **Scale:** Omni-sized data (152 weeks, about 1,800 demos) builds in **4.6 s**.
