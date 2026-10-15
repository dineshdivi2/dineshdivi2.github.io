"""Rebuild the publication HTML and figures from article.md and stored aggregates.

Install requirements-build.txt first. Alternatively install into .build-deps;
that checkout-local folder is ignored by Git.
"""
from pathlib import Path
import sys
import os
import re
import json
import html
import textwrap

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.build-deps'))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.build-deps' / '.mplconfig'))
import markdown
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ARTICLE = ROOT / 'articles' / '001-agent-cache-economics'
ASSETS = ARTICLE / 'assets'
URL = 'https://dineshdivi2.github.io/articles/001-agent-cache-economics/'
TITLE = 'The 88-Hour Cache Problem: KV Retention Economics for Agent Swarms'
REPO = 'https://github.com/dineshdivi2/swarm-kv-economics'
BLUE, TEAL, ORANGE, GRAY = '#276ba4', '#137777', '#be562e', '#62717e'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
                     'axes.labelcolor': '#304656', 'text.color': '#182f40', 'savefig.facecolor': 'white'})
D = json.loads((ROOT / 'source-data/essay-figure-data.json').read_text())


def save(fig, name):
    fig.savefig(ASSETS / name, dpi=180, bbox_inches='tight')
    plt.close(fig)


def figures():
    # All figures use the stored aggregates; this is not a rerun of the simulator.
    fig, ax = plt.subplots(figsize=(10, 3.4), layout='constrained')
    parts = list(D['bill']['usd'].values())
    labels = ['Missed input: length-derived repeat proxy', 'Other missed input', 'Cache hits', 'Output']
    left = 0
    for value, label, color in zip(parts, labels, [ORANGE, '#e3a584', BLUE, GRAY]):
        ax.barh(0, value, left=left, color=color, label=label, height=.5)
        ax.text(left + value / 2, 0, f'{100 * value / sum(parts):.0f}%', ha='center', va='center', color='white')
        left += value
    ax.set(yticks=[], xlabel='Illustrative cost (USD)', title='Reported token counters, repriced at Opus 5.5 rates')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.23), ncol=2, frameon=False, fontsize=8.5)
    ax.set_ylim(-.65, .65)
    save(fig, 'essay_b_input_bill.png')

    survival = json.loads((ROOT / 'source-data/survival.json').read_text())
    fig, ax = plt.subplots(figsize=(10, 4.8), layout='constrained')
    for (name, obj), color in zip(survival.items(), [BLUE, ORANGE, TEAL]):
        curve = [x for x in obj['curve'] if x['calls'] > 0]
        ax.step([max(1, x['lo_s']) / 60 for x in curve], [100 * x['survival'] for x in curve],
                where='post', label=name, color=color, linewidth=2)
    ax.set(xscale='log', xlim=(1 / 60, 1440), ylim=(0, 103), xlabel='Gap between request starts (minutes, log scale)',
           ylabel='Cached-token fraction (%)', title='Observed cached-token fractions by inter-call gap')
    ax.grid(alpha=.15)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    save(fig, 'v3_1_measured_survival.png')

    fig, ax = plt.subplots(figsize=(10, 4), layout='constrained')
    labels = ['Constructed large KV: 10 Gbps transfer', 'Constructed large KV: 7 GB/s transfer',
              'Large-layout recompute: assumed 5 seconds', 'Compact global KV only: 10 Gbps transfer',
              'Compact global KV only: 7 GB/s transfer']
    vals = list(D['restore']['seconds'].values())
    ys = np.arange(5)[::-1]
    ax.barh(ys, vals, color=[ORANGE, ORANGE, GRAY, BLUE, BLUE], height=.6)
    for y, value in zip(ys, vals):
        ax.text(value * 1.15, y, f'{value:.3g} s', va='center', fontsize=9)
    ax.set(xscale='log', xlim=(.005, 100), yticks=ys, yticklabels=labels,
           xlabel='Illustrative time (seconds, log scale)', title='KV size changes transfer arithmetic; full restore is not measured')
    ax.grid(axis='x', alpha=.15)
    save(fig, 'essay_f_restore_vs_recompute.png')

    fig, ax = plt.subplots(figsize=(10, 3.6), layout='constrained')
    for y, (name, duration) in enumerate([('Child A', 5), ('Child B', 15), ('Child C', 120)][::-1]):
        ax.barh(y, duration, height=.5, color=BLUE)
        ax.text(duration + 2, y, f'{duration} min', va='center', fontsize=9)
    ax.axvline(15, color=TEAL, linestyle='--', label='Two-of-three timing: 15 min')
    ax.axvline(120, color=ORANGE, linestyle='--', label='All-three timing: 120 min')
    ax.set(yticks=[0, 1, 2], yticklabels=['Child C', 'Child B', 'Child A'], xlim=(0, 145),
           xlabel='Time after launch (minutes)', title='A join rule changes the parent wait—and the completion condition')
    ax.legend(loc='upper center', bbox_to_anchor=(.5, -.2), ncol=2, frameon=False, fontsize=9)
    save(fig, 'essay_a_quorum_join.png')

    fig, ax = plt.subplots(figsize=(10, 4.5), layout='constrained')
    rows = D['keepalive_vs_best_native']
    labs = [r['label'].replace('Real sessions:', 'Replay:') for r in rows]
    for y, r in zip(np.arange(len(rows))[::-1], rows):
        ax.barh(y, r['point'], color=TEAL if r['kind'].startswith('simulated') else BLUE, height=.55)
        ax.errorbar(r['point'], y, xerr=[[max(0, r['point'] - r['lo'])], [max(0, r['hi'] - r['point'])]],
                    color='#182f40', capsize=3, linewidth=1)
        ax.text(max(r['hi'], r['point']) + 1.5, y, f"{r['point']:.1f}%", va='center', fontsize=9)
    ax.set(yticks=np.arange(len(rows))[::-1], yticklabels=labs, xlim=(0, 90),
           xlabel='Reduction in modeled input cost (%)', title='Forecast policy versus the cheaper passive native TTL')
    ax.grid(axis='x', alpha=.15)
    save(fig, 'essay_c_keepalive_vs_native.png')

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True, layout='constrained')
    g = D['guarantee_vs_keepalive']
    for ax, ttl in zip(axes, ['5 min TTL', '1 h TTL']):
        for offset, policy, color, label in [(-.16, 'forecast', BLUE, 'Keep-alive'), (.16, 'guarantee72', TEAL, 'Hypothetical 72 h guarantee')]:
            for y, key in enumerate(['S6-copilot', 'S6-tracelab']):
                row = g[f'{key}|{ttl}|{policy}']
                ax.barh(y + offset, row['point'], height=.29, color=color, label=label if y == 0 else None)
                ax.errorbar(row['point'], y + offset, xerr=[[row['point'] - row['lo']], [row['hi'] - row['point']]],
                            color='#182f40', capsize=3, linewidth=1)
        ax.set(title=ttl, xlabel='Modeled input-cost reduction (%)', xlim=(0, 50), yticks=[0, 1], yticklabels=['Copilot replay', 'TraceLab replay'])
        ax.grid(axis='x', alpha=.15)
    fig.suptitle('A hypothetical guarantee at an assumed one-hour write tariff', fontsize=12, fontweight='bold')
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(handles, labs, loc='outside lower center', ncol=2, frameon=False, fontsize=9)
    save(fig, 'essay_d_guarantee_vs_keepalive.png')

    bracket = json.loads((ROOT / 'source-data/deepseek-bracket.json').read_text())
    fig, axes = plt.subplots(1, len(bracket), figsize=(11, 4), sharey=True, layout='constrained')
    for ax, (family, cases) in zip(axes, bracket.items()):
        values = list(cases.values())
        x = np.arange(len(values))
        ax.bar(x - .17, [v['keepalive_vs_passive_pct'] for v in values], width=.34, color=BLUE, label='Keep-alive')
        ax.bar(x + .17, [v['guarantee_vs_passive_pct'] for v in values], width=.34, color=TEAL, label='Hypothetical guarantee')
        ax.set(title=family, xticks=x, xticklabels=['1 h', '6 h', '24 h', '72 h'], xlabel='Assumed passive retention', ylim=(0, 105))
        ax.grid(axis='y', alpha=.15)
    axes[0].set_ylabel('Modeled reduction vs passive (%)')
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(handles, labs, loc='outside lower center', ncol=2, frameon=False, fontsize=9)
    fig.suptitle('DeepSeek sensitivity scenarios—not measured API retention', fontsize=12, fontweight='bold')
    save(fig, 'essay_e_deepseek_bracket.png')


CAPTIONS = {
    'essay_b_input_bill.png': 'Figure 1. Reported Copilot token counters repriced at the modeled five-minute write, hit and output rates. The missed-input split uses prompt lengths; it does not identify repeated content.',
    'v3_1_measured_survival.png': 'Figure 2. Gap-binned cached-token fractions from adjacent same-model calls, capped at the smaller prompt length. These are not exact-prefix survival probabilities or evidence of maintenance uplift.',
    'essay_f_restore_vs_recompute.png': 'Figure 3. Illustrative transfer arithmetic for a constructed large KV layout and the reported compact global-KV component. Full restoration, replay, queueing and matched model performance are not measured.',
    'essay_a_quorum_join.png': 'Figure 4. Constructed timing example. A quorum is appropriate only when it satisfies the task; changing the join rule can change output quality and completeness.',
    'essay_c_keepalive_vs_native.png': 'Figure 5. Supplied v3 modeled input-cost reductions. Synthetic bars show three-seed ranges; replay bars show 90% session-bootstrap intervals. Retrospective feature labels limit replay interpretation.',
    'essay_d_guarantee_vs_keepalive.png': 'Figure 6. Supplied replay results against each panel’s passive TTL. The 72-hour guarantee and its one-hour write tariff are hypothetical. Error bars condition on model and extraction assumptions.',
    'essay_e_deepseek_bracket.png': 'Figure 7. Assumed retention curves and tariffs at the modeled peak rates. The guarantee case assumes 1% in-lifetime loss. No live API retention experiment was run.',
}

CSS = '''
:root{color-scheme:light;--ink:#182f40;--muted:#526777;--accent:#137777;--line:#dce5ea;--wash:#eef6f5}
*{box-sizing:border-box}html{scroll-padding-top:24px}body{margin:0;background:#f1f5f7;color:var(--ink);font:18px/1.75 Georgia,'Times New Roman',serif}
a{color:var(--accent);text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible{outline:3px solid #e8a347;outline-offset:4px}
.site-nav{max-width:1090px;margin:22px auto;padding:0 26px;display:flex;flex-wrap:wrap;gap:12px 24px;font:14px/1.5 system-ui,sans-serif}
main{max-width:1090px;margin:20px auto 64px;padding:42px 64px 54px;background:white;border:1px solid var(--line);border-radius:8px}
main>*{max-width:780px;margin-left:auto;margin-right:auto}h1{font-size:40px;line-height:1.16;letter-spacing:-.015em;margin:14px auto 20px;overflow-wrap:normal}
h2{font-size:26px;line-height:1.3;margin-top:44px;padding-top:16px;border-top:1px solid var(--line)}h3{font-size:21px;margin-top:28px;color:var(--accent)}
.meta,.contents,.footer,figcaption,.kicker{font:13px/1.65 system-ui,sans-serif;color:var(--muted)}.kicker{color:var(--accent);font-weight:700;letter-spacing:.06em;text-transform:uppercase}
.meta{display:flex;flex-wrap:wrap;gap:6px 18px;margin-bottom:22px}.contents{padding:14px 0;border-block:1px solid var(--line);margin-bottom:30px}.contents nav{columns:2;column-gap:26px;padding-top:10px}.contents a{display:block;padding:3px 0;break-inside:avoid;text-decoration:none}
summary{cursor:pointer;color:var(--accent);font-weight:600}blockquote{background:var(--wash);border-left:4px solid var(--accent);padding:12px 22px;border-radius:0 6px 6px 0}blockquote p{margin:5px 0}
figure{max-width:960px;margin-top:28px;margin-bottom:30px}figure img{width:100%;height:auto;border:1px solid var(--line);border-radius:6px}figcaption{margin-top:10px}
.table-wrap{overflow-x:auto;max-width:960px}table{border-collapse:collapse;width:100%;font:14px/1.6 system-ui,sans-serif}th,td{border-bottom:1px solid var(--line);padding:10px;text-align:left;vertical-align:top;min-width:140px}th{background:#f7fafb}
code{font:14px/1.5 ui-monospace,monospace;background:#f3f6f7;padding:2px 5px;border-radius:4px;overflow-wrap:anywhere}li{margin:8px 0}.footer{margin-top:38px;padding-top:18px;border-top:1px solid var(--line)}
.entry{padding:24px 0;border-block:1px solid var(--line);margin-top:28px}.entry h2{border:0;padding:0;margin:8px 0}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:8px;background:white;padding:8px;z-index:2}
@media(max-width:760px){main{padding:28px 20px;margin:12px 10px 40px}h1{font-size:31px}h2{font-size:24px}.contents nav{columns:1}.site-nav{padding:0 20px}}
@media print{body{background:white}main{margin:0;border:0;padding:0}.site-nav,.contents{display:none}h2,figure{break-inside:avoid}a{color:inherit}}
'''


def page(title, body, canonical, description, article=False):
    og_image = URL + 'assets/essay_b_input_bill.png'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>{html.escape(title)} · ArticleLog</title><meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style></head><body><a class="skip" href="#content">Skip to content</a>
<nav class="site-nav" aria-label="Site"><a href="/articles/">ArticleLog</a><a href="{REPO}">Simulation repository</a><a href="/">Earlier chart demo</a></nav>
<main id="content">{body}</main></body></html>'''


def build():
    figures()
    md = (ARTICLE / 'article.md').read_text(encoding='utf-8')
    assert md.splitlines()[0] == '# ' + TITLE
    body = markdown.markdown(md, extensions=['tables', 'toc', 'sane_lists'])
    def image(match):
        alt, src = match.groups()
        caption = CAPTIONS[Path(src).name]
        return f'<figure><a href="{src}" aria-label="Open figure: {html.escape(alt, quote=True)}"><img src="{src}" alt="{alt}" loading="lazy" decoding="async"></a><figcaption>{html.escape(caption)}</figcaption></figure>'
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)"\s*/?></p>', image, body)
    body = re.sub(r'(<table>.*?</table>)', r'<div class="table-wrap">\1</div>', body, flags=re.S)
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc = ''.join(f'<a href="#{ident}">{label}</a>' for ident, label in heads)
    words = len(re.sub('<[^>]+>', ' ', body).split())
    meta = f'<div class="kicker">ArticleLog 001 · Systems &amp; agents</div><div class="meta"><span>By Dinesh</span><time datetime="2026-10-16">16 October 2026</time><span>{round(words/230)} min read · 7 figures</span><span>Exploratory simulation</span></div>'
    toc_html = f'<details class="contents"><summary>In this article</summary><nav>{toc}</nav></details>'
    h1end = body.index('</h1>') + len('</h1>')
    body = meta + body[:h1end] + toc_html + body[h1end:]
    body += '<footer class="footer">ArticleLog 001 · Publication edition, 16 October 2026. Figures rebuilt from supplied v3 aggregates with corrected labels. <a href="article.md">Read the Markdown source</a> · <a href="https://github.com/dineshdivi2/dineshdivi2.github.io">Site source</a></footer>'
    description = 'Why long-running agents lose their cache, not their history—and when keeping it warm is worth paying for. An exploratory simulation with public coding-agent traces.'
    (ARTICLE / 'index.html').write_text(page(TITLE, body, URL, description, True), encoding='utf-8')
    index_body = f'''<div class="kicker">Dinesh · Technical writing</div><h1>ArticleLog</h1><p>Investigations into AI systems, agent workflows and the costs behind them.</p>
    <p class="meta">1 published article · Next entry: 002</p><article class="entry"><div class="meta">001 · 16 October 2026 · Exploratory simulation</div><h2><a href="001-agent-cache-economics/">{html.escape(TITLE)}</a></h2><p>{description}</p><p><a href="001-agent-cache-economics/">Read the article →</a></p></article>'''
    (ROOT / 'articles/index.html').write_text(page('ArticleLog', index_body, 'https://dineshdivi2.github.io/articles/', 'Technical articles by Dinesh.'), encoding='utf-8')
    (ROOT / 'articles/index.json').write_text(json.dumps({'series':'ArticleLog','published_count':1,'next_number':2,'entries':[{'number':1,'title':TITLE,'published_at':'2026-10-16','url':URL,'repository_url':REPO}]},indent=2),encoding='utf-8')
    print(json.dumps({'article':str(ARTICLE/'index.html'),'figures':len(CAPTIONS),'words':words,'title':TITLE}))


if __name__ == '__main__':
    build()
