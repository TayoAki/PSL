# Spike: data-driven demo hub on Astro Starlight

A throwaway proof of concept that checks the architecture proposed in
[`docs/03-build-plan.md`](../../docs/03-build-plan.md) before we commit to it. **This is not the
production scaffold.** Phase 1 of the plan starts a clean project and uses this code as a reference.

```bash
npm install
npm run build     # astro build + Pagefind index
npm run preview   # http://localhost:4321/demos/
```

## What it checks (all verified on 2026-09-28 with astro 7.3.5 and @astrojs/starlight 0.42.4)

| Question | Result |
|---|---|
| Can weekly pages be generated from **YAML data files** instead of hand-written MDX? | Yes. The `weeks` collection uses `glob()` over `src/content/demos/**/*.yaml`, and `src/pages/demos/[year]/[date].astro` renders each week with `<StarlightPage>`. |
| Do data-driven pages get Starlight's **right-hand table of contents**? | Yes. Pass `headings={[{ depth: 2, slug, text }]}` to `<StarlightPage>`; the TOC lists every demo anchor. |
| Can the **sidebar** (year groups, current year expanded) be generated from the data? | Yes. `astro.config.mjs` reads the folders at build start; 2026 renders `open` and 2025 collapsed. |
| Does **Pagefind** index these custom pages? | Yes. They carry `data-pagefind-body` and appear in the index (the 404 page is excluded). |
| Does **RSS** link to the weekly page with a stable `guid`? | Yes. `@astrojs/rss` items use the permalink as `link` and `guid`, and `publishedAt` as `pubDate`. |
| Does **bad data fail the build** with a useful message? | Yes. A malformed video ID fails with `demos.0.video.id: Invalid string: must match pattern`. An unknown presenter fails with `Invalid content reference … references "nobody-here" in collection "people", but that entry does not exist.` |
| Does it scale to Omni's archive size? | Yes. 152 synthetic weeks × 12 demos (≈1,800 demos) built 155 pages in **4.6 s**, and Pagefind indexed them in **0.36 s**, on a 4-vCPU container. |

One lesson: a regex can't prove a YouTube ID exists. `"not-a-video"` is 11 characters from
`[\w-]` and passes the pattern. The plan adds a draft-time `videos.list` check and a weekly
oEmbed availability check.

## Not covered by this spike

The lite YouTube facade (astro-embed), OG images, `.md` endpoints, `llms.txt`, the drafting
pipeline and all test tooling. Those are Phase 1–3 work in the plan.
