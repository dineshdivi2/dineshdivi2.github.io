# Dinesh — ArticleLog and BuildLog

- [ArticleLog index](https://dineshdivi2.github.io/articles/)
- [ArticleLog 001: The 88-Hour Cache Problem](https://dineshdivi2.github.io/articles/001-agent-cache-economics/)
- [Simulation repository](https://github.com/dineshdivi2/swarm-kv-economics)

The homepage links to ArticleLog at `/articles/` and BuildLog at `/builds/`. BuildLog has three basic project pages: Public Record, IrisFlow and yt2apple. Its numbering is independent of ArticleLog. The earlier Google chart embed has been removed.

BuildLog descriptions are grounded in the local project READMEs reviewed on 21 October 2026. Original X post links retain their earlier verified numbering; direct X retrieval was unavailable during this edit. These pages describe current documented capabilities, rather than reconstructing the exact release shown in each original post. Private repository links and raw source materials are not included.

## Build

Python 3.12 was used for this publication edition:

```bash
python -m pip install -r requirements-build.txt
python build_site.py
```

The script renders `articles/001-agent-cache-economics/article.md`, rebuilds seven PNG figures from the stored JSON aggregates in `source-data/`, and generates the article and index HTML. It does not rerun the underlying simulation or call model APIs. The aggregate sources are the v3 snapshot in the simulation repository; see that repository for extraction and simulation instructions.

For text and navigation edits, `python build_site.py --pages-only` keeps the existing figure files and regenerates HTML. Edit each `builds/<slug>/build.md` for project copy and `builds/index.json` for index metadata. Generated HTML is committed so GitHub Pages can serve it directly. This basic edition adds no new JavaScript or dependencies.

BuildLog validation, 21 October 2026: the existing Python 3.12 virtual environment successfully ran `build_site.py --pages-only`; seven HTML pages passed heading, language, main landmark, local-link and anchor checks. Article Markdown and ArticleLog metadata were unchanged. `git diff --check` passed. Localhost browser previews timed out in both the in-app browser and Chrome, so visual QA remains outstanding. This increment is prepared locally, not deployed.

Navigation and link-preview update, 21 October 2026: the homepage lists each entry with its status badge, the top bar names the site and marks the current section, and build pages link to the previous and next build. Every build also writes text-only 1200×630 share cards to `assets/og/` and the touch icon `assets/icon-180.png`; `favicon.svg` is hand-written. The cards and icon are generated with matplotlib and rebuild byte-for-byte identically. The article keeps its first figure as its share image. Checked with local headless-browser screenshots at desktop width, a 375px overflow check, and heading, metadata, local-link and anchor checks on all seven pages.

Original X posts are shown without X's embed script. `builds/index.json` stores each post's date and, where it has substantive text, the text with links and media removed. This was retrieved on 21 October 2026 from X's public oEmbed endpoint and matched each post's BuildLog number. Build pages quote that text in a card that links to the post; BuildLog 003's card shows only the date and link. List items show a "Posted" date that links to the post.

GitHub Pages serves the static files from `main` at `/`. `.nojekyll` bypasses Jekyll processing. Build dependencies and local environments are excluded from Git.

## Publication edition, 16 October 2026

This edition changes the title and corrects the interpretation and presentation of the original essay-v3 draft:

- Prompt-length reuse estimates are identified as proxies, not lower bounds or measured avoidable waste.
- Observational cached-token fractions are separated from exact-prefix survival and causal maintenance uplift.
- Compact global KV transfer arithmetic is separated from complete state restoration and provider TTL decisions.
- Replay feature leakage, the restricted oracle, timing assumptions and the hypothetical guarantee tariff are stated explicitly.
- Policy comparisons state their input-cost denominator and distinguish seed ranges from conditional bootstrap intervals.
- No unrun API probe is presented as an experiment result; no employer-resource declaration is made without evidence.
- All seven figures have corrected labels and visible captions. Primary sources and the public simulation are linked from the article.

Validation includes Python syntax, JSON and HTML parsing, local asset and anchor checks, figure inspection and narrow credential/placeholder scanning. The full simulator was not independently rerun for this publication.
