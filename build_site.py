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
import datetime

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
.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:8px;background:white;padding:8px;z-index:2}
.site-nav{align-items:baseline;font-size:15px}.site-nav .brand{margin-right:auto;color:var(--ink);font-weight:700;text-decoration:none}.site-nav a[aria-current]{color:var(--ink);font-weight:600;text-decoration-thickness:2px}
.section-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:4px 16px;margin-top:48px}.section-head h2{border:0;padding:0;margin:0}.section-head a{font:14px/1.5 system-ui,sans-serif}
.items{margin-top:20px}.item{padding:22px 0;border-top:1px solid var(--line)}.item :is(h2,h3){border:0;padding:0;margin:6px 0 4px;font-size:24px;line-height:1.3}.item :is(h2,h3) a{text-decoration:none}.item :is(h2,h3) a:hover{text-decoration:underline}.item p{margin:6px 0}
.item-meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;font:13px/1.6 system-ui,sans-serif;color:var(--muted)}.item-meta .kicker{font-size:12px}
.badge{display:inline-block;padding:2px 10px;border:1px solid #c5e0dd;border-radius:999px;background:var(--wash);color:#0f6262;font:600 12px/1.6 system-ui,sans-serif;white-space:nowrap}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}.x-icon{width:13px;height:13px;fill:currentColor;flex:none}.posted{display:inline-flex;align-items:center;gap:5px;color:var(--muted);text-decoration:none}.posted:hover{color:var(--accent);text-decoration:underline}
.post{margin-top:44px;padding:18px 22px;border:1px solid var(--line);border-radius:8px}.post-head{display:flex;align-items:center;gap:7px;margin:0 0 10px;font:13px/1.5 system-ui,sans-serif;color:var(--muted)}
.post blockquote{margin:0 0 12px;padding:0 0 0 16px;background:none;border-left:3px solid var(--accent);border-radius:0}.post blockquote p{margin:6px 0;font-size:17px;line-height:1.6}.post>a{font:14px/1.5 system-ui,sans-serif}
.pager{display:flex;flex-wrap:wrap;gap:16px;margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font:15px/1.5 system-ui,sans-serif}.pager a{text-decoration:none}.pager small{display:block;color:var(--muted);font-size:12px;letter-spacing:.06em;text-transform:uppercase}.pager .next{margin-left:auto;text-align:right}.pager+.footer{border-top:0;margin-top:14px}
.hero{position:relative;padding:18px 0 8px}.hero::before{content:'';position:absolute;inset:-42px -64px 0;z-index:0;pointer-events:none;background:radial-gradient(#cfdde3 1px,transparent 1.2px) 0 0/18px 18px;mask-image:linear-gradient(#000,transparent 92%);-webkit-mask-image:linear-gradient(#000,transparent 92%)}.hero>*{position:relative}
.hero h1{font-size:46px;font-weight:400;letter-spacing:-.02em;margin-bottom:14px}.hero h1 em{font-style:italic;color:var(--accent);background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 12' preserveAspectRatio='none'%3E%3Cpath d='M2 8c40-6 90-7 196-2' fill='none' stroke='%23e8a347' stroke-width='3' stroke-linecap='round'/%3E%3C/svg%3E") bottom/100% 10px no-repeat;padding-bottom:6px}
.hero .lede{color:var(--muted);font-size:19px;margin:0 0 18px}.now{display:inline-flex;align-items:center;gap:9px;padding:5px 14px;border:1px solid var(--line);border-radius:999px;background:white;font:13px/1.5 system-ui,sans-serif;color:var(--muted)}.now b{color:var(--ink);font-weight:600}
.dot{width:8px;height:8px;border-radius:50%;background:#e8a347;box-shadow:0 0 0 0 #e8a34780;animation:pulse 2.4s infinite}@keyframes pulse{70%{box-shadow:0 0 0 7px #e8a34700}100%{box-shadow:0 0 0 0 #e8a34700}}@media(prefers-reduced-motion:reduce){.dot{animation:none}}
.feature{display:grid;grid-template-columns:1.25fr 1fr;gap:26px;align-items:center;margin-top:22px;padding:24px;border:1px solid var(--line);border-radius:10px;background:linear-gradient(180deg,#fbfdfd,#fff)}.feature h3{font-size:26px;line-height:1.25;margin:8px 0 10px;color:var(--ink)}.feature h3 a{color:inherit;text-decoration:none}.feature h3 a:hover{text-decoration:underline}
.finding{margin:12px 0;padding-left:14px;border-left:3px solid #e8a347;font-style:italic;color:#304656}.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}.chip{padding:2px 10px;border-radius:6px;background:#f3f6f7;font:12px/1.7 system-ui,sans-serif;color:var(--muted)}
.feature figure{margin:0}.feature img{display:block;width:100%;border:1px solid var(--line);border-radius:6px}.read{font:600 14px/1.5 system-ui,sans-serif}
.next-entry{display:flex;gap:14px;align-items:baseline;margin-top:12px;padding:14px 18px;border:1px dashed #c9d6dc;border-radius:10px;font:14px/1.6 system-ui,sans-serif;color:var(--muted)}.next-entry b{color:var(--ink)}
.labels{margin-top:14px;font:12px/1.7 system-ui,sans-serif;color:var(--muted)}.labels span{margin-right:12px}.labels i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px;background:var(--accent)}
.sketches{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px;margin-top:18px}.sketch{display:flex;flex-direction:column;padding:18px;border:1px solid var(--line);border-radius:10px;background:#fcfbf7;text-decoration:none;color:var(--ink);transition:transform .15s,box-shadow .15s}.sketch:hover{transform:translateY(-2px);box-shadow:0 6px 18px #182f4012}
.sketch .no{font:12px/1.5 ui-monospace,monospace;color:var(--muted)}.sketch .gap{font-size:16px;line-height:1.5;margin:10px 0 12px}.sketch .gap::before{content:'“';color:#e8a347;font-size:26px;line-height:0;vertical-align:-8px;margin-right:2px}.sketch b{font:600 17px/1.4 system-ui,sans-serif}.sketch .what{font:14px/1.55 system-ui,sans-serif;color:var(--muted);margin:4px 0 14px;flex:1}.sketch .badge{align-self:flex-start}
.spark{margin:4px 0 18px;padding:14px 18px;background:#fcfbf7;border:1px solid var(--line);border-radius:8px;font-style:italic}.spark small{display:block;font:600 11px/1.6 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;font-style:normal;color:#b5762a}
@media(max-width:760px){.feature{grid-template-columns:1fr;padding:18px}.hero h1{font-size:34px}.hero::before{inset:-28px -20px 0}}
@media(max-width:760px){main{padding:28px 20px;margin:12px 10px 40px}h1{font-size:31px}h2{font-size:24px}.item :is(h2,h3){font-size:22px}.contents nav{columns:1}.site-nav{padding:0 20px}}
@media print{body{background:white}main{margin:0;border:0;padding:0}.site-nav,.contents{display:none}h2,figure{break-inside:avoid}a{color:inherit}}
'''


SITE = 'https://dineshdivi2.github.io'
SECTIONS = [('articles', '/articles/', 'ArticleLog'), ('builds', '/builds/', 'BuildLog')]


def page(title, body, canonical, description, article=False, section=None, card=None):
    """card names a generated 1200x630 share image in /assets/og/; the article keeps its own figure."""
    if card:
        social_image = (f'<meta property="og:image" content="{SITE}/assets/og/{card}.png"><meta property="og:image:width" content="1200">'
                        f'<meta property="og:image:height" content="630"><meta property="og:image:alt" content="{html.escape(title, quote=True)}">')
    elif canonical.startswith(URL):
        social_image = f'<meta property="og:image" content="{URL}assets/essay_b_input_bill.png">'
    else:
        social_image = ''
    full_title = title if section == 'home' else f'{title} · Dinesh'
    links = []
    for key, href, label in SECTIONS:
        current = '' if key != section else ' aria-current="page"' if canonical == SITE + href else ' aria-current="true"'
        links.append(f'<a href="{href}"{current}>{label}</a>')
    brand_current = ' aria-current="page"' if section == 'home' else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>{html.escape(full_title)}</title><meta name="description" content="{html.escape(description, quote=True)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/assets/icon-180.png" sizes="180x180"><link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="canonical" href="{canonical}"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:site_name" content="Dinesh">
<meta property="og:title" content="{html.escape(full_title if section == 'home' else title, quote=True)}"><meta property="og:description" content="{html.escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
{social_image}<meta name="twitter:card" content="{'summary_large_image' if social_image else 'summary'}">
<style>{CSS}</style></head><body><a class="skip" href="#content">Skip to content</a>
<nav class="site-nav" aria-label="Site"><a class="brand" href="/"{brand_current}>Dinesh</a>{''.join(links)}</nav>
<main id="content">{body}</main></body></html>'''


INK, MUTED = '#182f40', '#526777'


def share_card(name, kicker, title, subtitle, status=None):
    # Text-only 1200x630 card for link previews on X and elsewhere.
    fig = plt.figure(figsize=(12, 6.3), dpi=100)
    fig.patch.set_facecolor('white')
    fig.add_artist(matplotlib.patches.Rectangle((0, 0), .014, 1, color=TEAL, transform=fig.transFigure))
    fig.text(.075, .84, kicker.upper(), color=TEAL, fontsize=15, fontweight='bold', family='DejaVu Sans')
    lines = title.split('\n') if '\n' in title else textwrap.wrap(title, 30)
    fig.text(.075, .76, '\n'.join(lines), color=INK, fontsize=40, fontweight='bold', family='DejaVu Serif',
             va='top', linespacing=1.2)
    sub = textwrap.wrap(subtitle, 62)[:2]
    fig.text(.075, .76 - .123 * len(lines) - .05, '\n'.join(sub), color=MUTED, fontsize=18, family='DejaVu Sans',
             va='top', linespacing=1.45)
    if status:
        fig.text(.075, .1, status, color='#0f6262', fontsize=15, fontweight='bold', family='DejaVu Sans',
                 bbox={'boxstyle': 'round,pad=.5,rounding_size=.9', 'facecolor': '#eef6f5', 'edgecolor': '#c5e0dd'})
    fig.text(.925, .1, 'dineshdivi2.github.io', color=MUTED, fontsize=15, family='DejaVu Sans', ha='right')
    out = ROOT / 'assets' / 'og'
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f'{name}.png', dpi=100, metadata={'Software': None})
    plt.close(fig)


def icon():
    fig = plt.figure(figsize=(1.8, 1.8), dpi=100)
    fig.text(.5, .47, 'D', color='white', fontsize=82, fontweight='bold', family='DejaVu Serif', ha='center', va='center')
    fig.savefig(ROOT / 'assets' / 'icon-180.png', dpi=100, facecolor=TEAL, metadata={'Software': None})
    plt.close(fig)


def build():
    if '--pages-only' not in sys.argv:
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
    (ARTICLE / 'index.html').write_text(page(TITLE, body, URL, description, True, section='articles'), encoding='utf-8')
    article_item = f'''<article class="item"><div class="item-meta"><span>ArticleLog 001</span><time datetime="2026-10-16">16 October 2026</time><span class="badge">Exploratory simulation</span></div>
    <TAG><a href="/articles/001-agent-cache-economics/">{html.escape(TITLE)}</a></TAG><p>{description}</p></article>'''
    index_body = f'''<div class="kicker">Dinesh · Technical writing</div><h1>ArticleLog</h1><p>Investigations into AI systems, agent workflows and the costs behind them.</p>
    <p class="meta">1 published article · Next entry: 002</p><div class="items">{article_item.replace('TAG', 'h2')}</div>'''
    (ROOT / 'articles/index.html').write_text(page('ArticleLog', index_body, SITE + '/articles/', 'Technical articles by Dinesh.', section='articles', card='articles'), encoding='utf-8')
    builds = build_logs()
    home_description = 'Working notes on AI systems by Dinesh: long-form investigations, plus small product sketches built along the way.'
    feature = f'''<article class="feature"><div><div class="item-meta"><span>ArticleLog 001</span><time datetime="2026-10-16">16 Oct 2026</time><span class="badge">Exploratory simulation</span></div>
    <h3><a href="/articles/001-agent-cache-economics/">{html.escape(TITLE)}</a></h3>
    <p class="finding">Your agent remembers the whole conversation. The provider's cache forgot it an hour ago, and you pay to rebuild it. Whether that's worth fixing depends on how the agent waits.</p>
    <div class="chips"><span class="chip">{round(words/230)} min read</span><span class="chip">7 figures</span><span class="chip">1.0M trace calls</span><span class="chip">Reproducible repo</span></div>
    <p><a class="read" href="/articles/001-agent-cache-economics/">Read the investigation →</a></p></div>
    <figure><a href="/articles/001-agent-cache-economics/" tabindex="-1" aria-hidden="true"><img src="/articles/001-agent-cache-economics/assets/v3_1_measured_survival.png" alt="" loading="lazy"></a></figure></article>'''
    home = f'''<header class="hero"><div class="kicker">Dinesh · Working notes</div><h1>Building things, writing down what I <em>learn</em>.</h1>
    <p class="lede">Mostly AI systems. When something doesn't add up, I keep digging until it does, then write it down. Now and then I build the thing I wished existed.</p>
    <span class="now"><span class="dot" aria-hidden="true"></span><span><b>Now writing:</b> ArticleLog 002, on what changes when a cache comes with a promise</span></span></header>
    <section aria-labelledby="articlelog"><div class="section-head"><h2 id="articlelog">ArticleLog</h2><a href="/articles/">All articles →</a></div>
    <p>Small things I noticed and followed further than I meant to. Measured where I could, labelled where I couldn't.</p>{feature}
    <div class="next-entry"><b>002</b><span>In progress: a prompt cache used to be "best effort". What happens when it becomes a promise?</span></div>
    <p class="labels"><span><i></i>Every entry carries an evidence label</span><span>Exploratory · Measured · Documentation analysis · Opinion</span></p></section>
    <section aria-labelledby="buildlog"><div class="section-head"><h2 id="buildlog">BuildLog</h2><a href="/builds/">All sketches →</a></div>
    <p>Things I wished existed, so I built a rough version. Rough on purpose. Mostly.</p><div class="sketches">{''.join(sketch(e) for e in builds)}</div></section>
    <footer class="footer"><a href="https://x.com/getsetahead">Follow on X</a> · <a href="https://github.com/dineshdivi2">GitHub</a></footer>'''
    (ROOT / 'index.html').write_text(page('Dinesh — Working notes on AI systems', home, SITE + '/', home_description, section='home', card='home'), encoding='utf-8')
    share_card('home', 'Dinesh · Working notes', 'Building things, writing\ndown what I learn.', home_description)
    share_card('articles', 'Dinesh · Technical writing', 'ArticleLog', 'Investigations into AI systems, agent workflows and the costs behind them.')
    icon()
    (ROOT / 'articles/index.json').write_text(json.dumps({'series':'ArticleLog','published_count':1,'next_number':2,'entries':[{'number':1,'title':TITLE,'published_at':'2026-10-16','url':URL,'repository_url':REPO}]},indent=2),encoding='utf-8')
    print(json.dumps({'article':str(ARTICLE/'index.html'),'figures':len(CAPTIONS),'words':words,'title':TITLE}))


X_ICON = ('<svg class="x-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>')


def post_date(entry, month='%B'):
    day = datetime.date.fromisoformat(entry['post_date'])
    return f'{day.day} {day:{month} %Y}'


def build_item(entry, tag):
    route = '/builds/' + entry['slug'] + '/'
    posted = (f'<a class="posted" href="{entry["post_url"]}">{X_ICON}<span>Posted <time datetime="{entry["post_date"]}">{post_date(entry, "%b")}</time>'
              f'<span class="sr-only"> on X</span></span></a>')
    return (f'<article class="item"><div class="item-meta"><span>BuildLog {entry["number"]:03d}</span><span class="badge">{html.escape(entry["status"])}</span>{posted}</div>'
            f'<{tag}><a href="{route}">{html.escape(entry["title"])}</a></{tag}><p>{html.escape(entry["description"])}</p></article>')


def sketch(entry):
    # Casual card: the missing thing first, then what was built and where it stands.
    return (f'<a class="sketch" href="/builds/{entry["slug"]}/"><span class="no">BuildLog {entry["number"]:03d} · {post_date(entry, "%b")}</span>'
            f'<span class="gap">{html.escape(entry["gap"])}</span><b>{html.escape(entry["title"])}</b>'
            f'<span class="what">{html.escape(entry["description"])}</span><span class="badge">{html.escape(entry["status"])}</span></a>')


def build_logs():
    directory = ROOT / 'builds'
    data = json.loads((directory / 'index.json').read_text(encoding='utf-8'))
    entries = data['entries']
    for i, entry in enumerate(entries):
        folder = directory / entry['slug']
        source = (folder / 'build.md').read_text(encoding='utf-8')
        body = markdown.markdown(source, extensions=['sane_lists'])
        label = f"BuildLog {entry['number']:03d}"
        h1end = body.index('</h1>') + len('</h1>')
        body = body[:h1end] + f'<p class="spark"><small>The missing thing</small>{html.escape(entry["gap"])}</p>' + body[h1end:]
        body = f'<div class="item-meta"><span class="kicker">{label}</span><span class="badge">{html.escape(entry["status"])}</span></div>' + body
        pager = []
        if i > 0:
            prev = entries[i - 1]
            pager.append(f'<a class="prev" href="/builds/{prev["slug"]}/"><small>Previous</small>← {prev["number"]:03d} · {html.escape(prev["title"])}</a>')
        if i < len(entries) - 1:
            nxt = entries[i + 1]
            pager.append(f'<a class="next" href="/builds/{nxt["slug"]}/"><small>Next</small>{nxt["number"]:03d} · {html.escape(nxt["title"])} →</a>')
        # BuildLog 003's post is a bare link, so its card shows only the date and link.
        quote = ''.join(f'<p>{html.escape(line)}</p>' for line in entry.get('post_text', []))
        body += (f'<aside class="post" aria-label="Original post on X"><p class="post-head">{X_ICON}<span>@getsetahead · Posted '
                 f'<time datetime="{entry["post_date"]}">{post_date(entry)}</time></span></p>'
                 + (f'<blockquote>{quote}</blockquote>' if quote else '')
                 + f'<a href="{entry["post_url"]}">View the original {label} post on X →</a></aside>')
        body += f'<nav class="pager" aria-label="More builds">{"".join(pager)}</nav>'
        body += '<footer class="footer"><a href="/builds/">All builds</a></footer>'
        route = '/builds/' + entry['slug'] + '/'
        (folder / 'index.html').write_text(page(entry['title'], body, SITE + route, entry['description'], section='builds', card=entry['slug']), encoding='utf-8')
        share_card(entry['slug'], label, entry['title'], entry['description'], entry['status'])
    intro = 'Things I wished existed, so I sketched a working version. Each one starts from a missing product or feature and stays honest about how rough it is.'
    body = f'<div class="kicker">Dinesh · Product sketches</div><h1>BuildLog</h1><p>{intro}</p><div class="sketches">' + ''.join(sketch(e) for e in entries) + '</div>'
    (directory / 'index.html').write_text(page('BuildLog', body, SITE + '/builds/', 'Projects by Dinesh: Public Record, IrisFlow and yt2apple.', section='builds', card='builds'), encoding='utf-8')
    share_card('builds', 'Dinesh · Projects', 'BuildLog', intro)
    return entries


if __name__ == '__main__':
    build()
