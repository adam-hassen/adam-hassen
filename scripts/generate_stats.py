"""Génère les graphiques de statistiques du profil GitHub (SVG, aux couleurs du profil).

Utilisé par .github/workflows/stats.yml. Test local : python scripts/generate_stats.py --demo
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request
from collections import OrderedDict

OUT = "stats-out"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
ACC, LIGHT, MUTED, TXT = "#2F7FC1", "#7CC4FF", "#8B949E", "#E6EDF3"
MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
e = html.escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"Erreur API GitHub : {data['errors']}")
    return data["data"]["user"]


def demo():
    today = dt.date.today()
    days = [{"date": (today - dt.timedelta(days=i)).isoformat(),
             "contributionCount": (i * 7) % 5 if i % 3 else 0} for i in range(364)]
    return {
        "followers": {"totalCount": 2},
        "repositories": {"totalCount": 18, "nodes": [
            {"stargazerCount": 3, "languages": {"edges": [
                {"size": 900, "node": {"name": "Jupyter Notebook", "color": "#DA5B0B"}},
                {"size": 600, "node": {"name": "Python", "color": "#3572A5"}},
                {"size": 300, "node": {"name": "Java", "color": "#b07219"}},
                {"size": 250, "node": {"name": "TypeScript", "color": "#3178c6"}},
                {"size": 150, "node": {"name": "HTML", "color": "#e34c26"}},
                {"size": 120, "node": {"name": "CSS", "color": "#563d7c"}},
                {"size": 60, "node": {"name": "C++", "color": "#f34b7d"}}]}}]},
        "contributionsCollection": {
            "totalCommitContributions": 180, "totalPullRequestContributions": 6,
            "restrictedContributionsCount": 0,
            "contributionCalendar": {"totalContributions": 254,
                                     "weeks": [{"contributionDays": days}]}},
    }


def card(w, h, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0F1B2D"/><stop offset="1" stop-color="#0D1117"/></linearGradient>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{LIGHT}"/></linearGradient>
<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{LIGHT}"/></linearGradient></defs>
<style>.c{{animation:in .8s ease-out both}}@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.grow{{transform-box:fill-box;transform-origin:bottom;animation:gr 1s ease-out both}}@keyframes gr{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.wide{{transform-box:fill-box;transform-origin:left;animation:wd 1s ease-out both}}@keyframes wd{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}</style>
<g class="c"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="url(#g)" stroke="#223246"/>
<rect x="1" y="1" width="{w-2}" height="4" rx="2" fill="url(#a)"/>
<text x="28" y="44" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2" fill="{LIGHT}">{e(title)}</text>
{body}</g></svg>'''


def kpis(u):
    c = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    items = [
        ("Contributions (12 mois)", c["contributionCalendar"]["totalContributions"]),
        ("Commits (12 mois)", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
        ("Dépôts publics", u["repositories"]["totalCount"]),
        ("Étoiles reçues", stars),
    ]
    w, h, tw = 1200, 170, 277
    parts = []
    for i, (label, val) in enumerate(items):
        x = 28 + i * (tw + 12)
        parts.append(f'<rect x="{x}" y="62" width="{tw}" height="84" rx="10" fill="{ACC}" fill-opacity="0.08" stroke="{ACC}" stroke-opacity="0.35"/>'
                     f'<text x="{x+20}" y="106" font-family="{FONT}" font-size="34" font-weight="800" fill="#FFFFFF">{val}</text>'
                     f'<text x="{x+20}" y="132" font-family="{FONT}" font-size="14" fill="{MUTED}">{e(label)}</text>')
    return card(w, h, "".join(parts), "EN CHIFFRES")


def languages(u):
    tot = OrderedDict()
    colors = {}
    for r in u["repositories"]["nodes"]:
        for ed in r["languages"]["edges"]:
            n = ed["node"]["name"]
            tot[n] = tot.get(n, 0) + ed["size"]
            colors[n] = ed["node"]["color"] or ACC
    top = sorted(tot.items(), key=lambda x: -x[1])[:6]
    s = sum(v for _, v in top) or 1
    w, h = 590, 330
    parts, y = [], 84
    for i, (n, v) in enumerate(top):
        pct = v / s * 100
        bw = max(4, 290 * pct / 100)
        parts.append(f'<text x="28" y="{y+14}" font-family="{FONT}" font-size="15" font-weight="600" fill="{TXT}">{e(n)}</text>'
                     f'<rect x="200" y="{y+2}" width="290" height="14" rx="7" fill="#FFFFFF" fill-opacity="0.06"/>'
                     f'<rect class="wide" style="animation-delay:{i*0.12:.2f}s" x="200" y="{y+2}" width="{bw:.0f}" height="14" rx="7" fill="{colors[n]}"/>'
                     f'<text x="562" y="{y+14}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">{pct:.1f} %</text>')
        y += 40
    return card(w, h, "".join(parts), "LANGAGES LES PLUS UTILISÉS")


def activity(u):
    counts = OrderedDict()
    today = dt.date.today()
    for k in range(11, -1, -1):
        m = (today.month - 1 - k) % 12 + 1
        yy = today.year + ((today.month - 1 - k) // 12)
        counts[(yy, m)] = 0
    for wk in u["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in wk["contributionDays"]:
            dd = dt.date.fromisoformat(d["date"])
            if (dd.year, dd.month) in counts:
                counts[(dd.year, dd.month)] += d["contributionCount"]
    w, h = 590, 330
    base, top_, left, right = 280, 80, 28, 562
    mx = max(counts.values()) or 1
    step = (right - left) / 12
    bw = step * 0.62
    parts = [f'<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="#223246"/>']
    for i, ((yy, m), v) in enumerate(counts.items()):
        x = left + i * step + (step - bw) / 2
        bh = (base - top_) * v / mx
        if v:
            parts.append(f'<rect class="grow" style="animation-delay:{i*0.06:.2f}s" x="{x:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="url(#bar)"/>'
                         f'<text x="{x+bw/2:.1f}" y="{base-bh-6:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TXT}">{v}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{base+20}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">{MOIS[m-1]}</text>')
    return card(w, h, "".join(parts), "ACTIVITÉ MENSUELLE")


def main():
    if "--demo" in sys.argv:
        u = demo()
    else:
        u = fetch(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("stats-chiffres", kpis), ("stats-langages", languages), ("stats-activite", activity)):
        with open(f"{OUT}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(fn(u))
    print("Graphiques générés dans", OUT)


if __name__ == "__main__":
    main()
