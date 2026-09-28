#!/usr/bin/env python3
"""Reproduce the quantitative teardown of https://docs.omni.co/demos.

Reads the public sitemap, the markdown export of every weekly demo page
(Mintlify serves `<page>.md`), and the demos RSS feed, then prints per-year
statistics: weeks, videos, videos per week, embed providers, bylines and
RSS publish lag. Standard library only.

Usage:
    python3 research/omni_demos_stats.py                # table to stdout
    python3 research/omni_demos_stats.py --json out.json
    python3 research/omni_demos_stats.py --cache-dir .cache/omni
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import email.utils
import json
import pathlib
import re
import statistics
import sys
import urllib.request

BASE = "https://docs.omni.co"
USER_AGENT = "demo-hub-research/1.0 (+https://github.com/tayoaki/psl)"
WEEKLY_URL = re.compile(r"^https://docs\.omni\.co/demos/(\d{4})/(\d{8})$")
IFRAME_SRC = re.compile(r'<iframe[^>]*\ssrc="([^"]+)"')
H2 = re.compile(r"^## (.+)$", re.M)
# Byline formats used over time:
#   2023-10 .. 2026-02  *Name · `tag` `tag`*    (2024-07/08 without the name: *`Tag` `Tag`*)
#   2026-03 ..          *`Name · Tag Tag`*      (tags no longer delimited)
BYLINE_DELIMITED = re.compile(r"^\*([^*`·\n]+?)\s*·\s*((?:`[^`]+`\s*)+)\*\s*$", re.M)
BYLINE_TAGS_ONLY = re.compile(r"^\*((?:`[^`·]+`\s*)+)\*\s*$", re.M)
BYLINE_SINGLE_SPAN = re.compile(r"^\*`([^`·]+?)\s*·\s*([^`]+)`\*\s*$", re.M)


def parse_bylines(md: str) -> list[dict]:
    """Return [{presenter, tags, delimited}] for every byline on a weekly page."""
    out = []
    for name, tags in BYLINE_DELIMITED.findall(md):
        out.append({"presenter": name.strip(), "tags": re.findall(r"`([^`]+)`", tags), "delimited": True})
    for tags in BYLINE_TAGS_ONLY.findall(md):
        out.append({"presenter": None, "tags": re.findall(r"`([^`]+)`", tags), "delimited": True})
    for name, label in BYLINE_SINGLE_SPAN.findall(md):
        out.append({"presenter": name.strip(), "tags": [label.strip()], "delimited": False})
    return out


def fetch(url: str, cache_dir: pathlib.Path | None) -> str:
    if cache_dir:
        cached = cache_dir / re.sub(r"[^A-Za-z0-9._-]", "_", url)
        if cached.exists():
            return cached.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cached.write_text(body, encoding="utf-8")
    return body


def weekly_urls(cache_dir: pathlib.Path | None) -> list[str]:
    sitemap = fetch(f"{BASE}/sitemap.xml", cache_dir)
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    return sorted(u for u in locs if WEEKLY_URL.match(u))


def analyze_week(url: str, cache_dir: pathlib.Path | None) -> dict:
    year, ymd = WEEKLY_URL.match(url).groups()
    md = fetch(f"{url}.md", cache_dir)
    srcs = IFRAME_SRC.findall(md)
    hosts = collections.Counter(re.sub(r"^https?://(www\.)?([^/]+)/.*$", r"\2", s) for s in srcs)
    return {
        "url": url,
        "year": year,
        "date": ymd,
        "weekday": dt.datetime.strptime(ymd, "%Y%m%d").strftime("%A"),
        "videos": len(srcs),
        "hosts": dict(hosts),
        "sections": len(H2.findall(md)),
        "bylines": parse_bylines(md),
        "youtube_ids": re.findall(r"youtube(?:-nocookie)?\.com/embed/([\w-]{11})", md),
    }


def rss_lag(cache_dir: pathlib.Path | None) -> list[dict]:
    rss = fetch(f"{BASE}/demos/rss.xml", cache_dir)
    rows = []
    for item in re.findall(r"<item>.*?</item>", rss, flags=re.S):
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]>", item).group(1)
        published = email.utils.parsedate_to_datetime(re.search(r"<pubDate>(.*?)</pubDate>", item).group(1))
        demo_day = dt.datetime.strptime(title, "%B %d, %Y").replace(tzinfo=dt.timezone.utc)
        rows.append({
            "title": title,
            "link": re.search(r"<link>(.*?)</link>", item).group(1),
            "published": published.isoformat(),
            "lag_days": round((published - demo_day).total_seconds() / 86400, 1),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cache-dir", type=pathlib.Path, help="cache fetched pages here")
    parser.add_argument("--json", type=pathlib.Path, help="also write raw results to this file")
    parser.add_argument("--concurrency", type=int, default=4)
    args = parser.parse_args()

    urls = weekly_urls(args.cache_dir)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        weeks = list(pool.map(lambda u: analyze_week(u, args.cache_dir), urls))
    feed = rss_lag(args.cache_dir)

    by_year: dict[str, list[dict]] = collections.defaultdict(list)
    for w in weeks:
        by_year[w["year"]].append(w)

    print(f"{'year':<6}{'weeks':>6}{'videos':>8}{'median/wk':>11}{'min':>5}{'max':>5}{'presenters':>12}  hosts")
    for year in sorted(by_year):
        ws = by_year[year]
        per_week = [w["videos"] for w in ws]
        hosts = collections.Counter()
        for w in ws:
            hosts.update(w["hosts"])
        presenters = {b["presenter"] for w in ws for b in w["bylines"] if b["presenter"]}
        print(f"{year:<6}{len(ws):>6}{sum(per_week):>8}{statistics.median(per_week):>11}"
              f"{min(per_week):>5}{max(per_week):>5}{len(presenters):>12}  {dict(hosts)}")

    all_ids = [i for w in weeks for i in w["youtube_ids"]]
    weekdays = collections.Counter(w["weekday"] for w in weeks)
    lags = [r["lag_days"] for r in feed]
    bylines = [b for w in weeks for b in w["bylines"]]
    tags = collections.Counter(t.strip() for b in bylines if b["delimited"] for t in b["tags"])
    folded = collections.defaultdict(set)
    for t in tags:
        folded[t.lower()].add(t)
    print(f"\nweekly pages: {len(weeks)}  videos: {sum(w['videos'] for w in weeks)}  "
          f"unique YouTube ids: {len(set(all_ids))}")
    print(f"bylines: {len(bylines)} on {sum(1 for w in weeks if w['bylines'])} weeks; "
          f"distinct presenters: {len({b['presenter'] for b in bylines if b['presenter']})}")
    print(f"delimited tags: {len(tags)} distinct, {len(folded)} after case-folding, "
          f"{sum(1 for v in folded.values() if len(v) > 1)} case-variant groups; "
          f"undelimited bylines (tags run together): {sum(1 for b in bylines if not b['delimited'])}")
    print(f"demo-day weekdays: {dict(weekdays)}")
    if lags:
        print(f"RSS: {len(feed)} items, publish lag after demo day {min(lags)}-{max(lags)} days "
              f"(median {statistics.median(lags)}); items link to {feed[0]['link']}")

    if args.json:
        args.json.write_text(json.dumps({"weeks": weeks, "rss": feed}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
