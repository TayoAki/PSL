# PSL — Demo Hub

Research and plan for building our own weekly video-demo hub, modelled on
[docs.omni.co/demos](https://docs.omni.co/demos). Every Friday the team records short feature
demos. By Monday they're published as one page per week (title, presenter and tags, summary,
video), with an index, year archives, an RSS feed and search.

## Documents

| | |
|---|---|
| [docs/01-how-omni-demos-works.md](docs/01-how-omni-demos-works.md) | Teardown of Omni's page: structure, components, feeds, numbers (150 weeks, 1,787 videos), publishing workflow and the weaknesses we'll fix |
| [docs/02-open-source-landscape.md](docs/02-open-source-landscape.md) | Open-source frameworks, reference implementations and pipeline tools, compared and ranked |
| [docs/03-build-plan.md](docs/03-build-plan.md) | **The plan**: decisions, architecture, content model, pipeline, step-by-step phases, timeline, costs, risks |
| [docs/04-test-plan.md](docs/04-test-plan.md) | How we test it: content validation, unit, build-output, E2E, accessibility, performance, LLM evals, CI wiring |

## Recommendation in one paragraph

**Site:** an **Astro Starlight** static site where each week is **one YAML file**. The index,
year archives, sidebar, "latest" callout, RSS, search index, `.md` exports and `llms.txt` are
all generated from those files.

**Pipeline:** a **TypeScript pipeline in GitHub Actions**. It reads the week's Unlisted YouTube
videos, gets transcripts and asks Claude for a summary, tags and sensitive-content flags. Then it
opens a **PR that an editor reviews and merges**. On merge the site deploys and the videos go
Public.

**Cost and effort:** about 17–24 engineer-days to build and about $0–10/month to run.
Section 10 of the build plan covers the Mintlify alternative, which gives exact Omni parity.

## Research artefacts

- [`research/omni_demos_stats.py`](research/omni_demos_stats.py) regenerates every number in
  the teardown from Omni's public sitemap, markdown exports and RSS. It uses only the standard
  library and takes about 20 seconds:

  ```bash
  python3 research/omni_demos_stats.py
  ```
- [`research/spike-starlight/`](research/spike-starlight/) is a throwaway spike that proves the
  recommended architecture: data-driven weekly pages, TOC, generated sidebar, Pagefind, RSS,
  and build failures on bad data. It builds Omni-scale data (about 1,800 demos) in 4.6 s.

  ```bash
  cd research/spike-starlight && npm install && npm run build
  ```
