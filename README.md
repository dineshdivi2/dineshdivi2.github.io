# Articles and earlier chart demo

- [ArticleLog index](https://dineshdivi2.github.io/articles/)
- [ArticleLog 001: The 88-Hour Cache Problem](https://dineshdivi2.github.io/articles/001-agent-cache-economics/)
- [Simulation repository](https://github.com/dineshdivi2/swarm-kv-economics)

The original root chart demo remains in place, with links to the article section added above it.

## Build

Python 3.12 was used for this publication edition:

```bash
python -m pip install -r requirements-build.txt
python build_site.py
```

The script renders `articles/001-agent-cache-economics/article.md`, rebuilds seven PNG figures from the stored JSON aggregates in `source-data/`, and generates the article and index HTML. It does not rerun the underlying simulation or call model APIs. The aggregate sources are the v3 snapshot in the simulation repository; see that repository for extraction and simulation instructions.

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
