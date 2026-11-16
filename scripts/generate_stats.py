"""Génère les graphiques de statistiques du profil (SVG animés, thème clair et sombre).

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
ACC, LIGHT, MUTED, TXT = "#6E7BFF", "#B8C4FF", "#8C93AE", "#F2F4FF"
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
             "contributionCount": (i * 7) % 5 if i % 3 else 0} for i in range(363, -1, -1)]
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




# ───────────── thème : fond transparent, couleurs suivant le mode clair / sombre ─────────────
CSS = f"""
:root{{--card:#FFFFFF;--line:#E3E8F2;--ink:#111A33;--muted:#6B7592;--rule:#EDF0F6;--track:#EEF1F7;--acc:#2F5BEA;--acc2:#0E9F8F}}
@media (prefers-color-scheme:dark){{:root{{--card:#10162A;--line:#242C44;--ink:#EEF2FB;--muted:#8A94AF;--rule:#1E2640;--track:#1A2238;--acc:#7C9CFF;--acc2:#3CCFBE}}}}
.card{{fill:var(--card);stroke:var(--line)}}
.t{{fill:var(--ink);font:650 19px {FONT}}}
.big{{fill:var(--ink);font:700 30px {FONT};letter-spacing:-.5px}}
.lbl{{fill:var(--ink);font:500 14px {FONT}}}
.m{{fill:var(--muted);font:400 12.5px {FONT}}}
.rule{{stroke:var(--rule)}}
.track{{fill:var(--track)}}
.bar{{fill:var(--acc);transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.3,0,.2,1) forwards}}
.line{{fill:none;stroke:var(--acc);stroke-width:2.2;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.4s cubic-bezier(.45,0,.2,1) .2s forwards}}
.area{{fill:var(--acc);opacity:0;animation:area 1s ease-out 2.2s forwards}}
.pt{{fill:var(--acc2)}}
.halo{{fill:none;stroke:var(--acc2);stroke-width:1.5;transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes area{{to{{opacity:.08}}}}
@keyframes pulse{{0%{{transform:scale(1);opacity:.8}}100%{{transform:scale(3.2);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.bar{{transform:none}}.line{{stroke-dashoffset:0}}.area{{opacity:.08}}}}
"""


def svg(w, h, body, label, px=32, py=30):
    W, H = w + 2 * px, h + 2 * py
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">'
            f'<style>{CSS}</style><rect class="card" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16"/>'
            f'<g transform="translate({px} {py})">{body}</g></svg>')


def languages(u):
    tot = OrderedDict()
    for r in u["repositories"]["nodes"]:
        for ed in r["languages"]["edges"]:
            n = ed["node"]["name"]
            tot[n] = tot.get(n, 0) + ed["size"]
    top = sorted(tot.items(), key=lambda x: -x[1])[:6]
    s = sum(v for _, v in top) or 1
    w, h = 560, 280
    parts, y = [f'<text class="t" x="0" y="24">Langages</text>'], 66
    for i, (n, v) in enumerate(top):
        pct = v / s * 100
        bw = max(3, 320 * pct / 100)
        parts.append(f'<text class="lbl" x="0" y="{y+12}">{e(n)}</text>'
                     f'<rect class="track" x="180" y="{y}" width="320" height="12" rx="6"/>'
                     f'<rect class="bar" style="animation-delay:{.2 + i*.12:.2f}s;opacity:{1 - i*0.12:.2f}" x="180" y="{y}" width="{bw:.0f}" height="12" rx="6"/>'
                     f'<text class="m" x="{w}" y="{y+11}" text-anchor="end">{pct:.0f} %</text>')
        y += 38
    return svg(w, h, "".join(parts), "Langages les plus utilisés")


def smooth(pts, lo, hi):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(max(p1[1] + (p2[1] - p0[1]) / 6, lo), hi))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(max(p2[1] - (p3[1] - p1[1]) / 6, lo), hi))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def contributions(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for wk in cal["weeks"] for d in wk["contributionDays"]]
    weeks, labels, last = [], [], None
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append(sum(d["contributionCount"] for d in chunk))
        m = dt.date.fromisoformat(chunk[0]["date"]).month
        labels.append(MOIS[m - 1] if m != last else "")
        last = m
    w, h = 560, 280
    left, right, top, base = 0, w, 92, h - 34
    mx = max(weeks) or 1
    n = len(weeks)
    pts = [(left + (right - left) * i / max(1, n - 1), base - (base - top) * v / mx) for i, v in enumerate(weeks)]
    d = smooth(pts, top - 6, base)
    parts = [f'<text class="t" x="0" y="24">Contributions sur 12 mois</text>',
             f'<text class="big" x="0" y="66">{cal["totalContributions"]}</text>',
             f'<text class="m" x="{w}" y="66" text-anchor="end">par semaine, pic à {mx}</text>']
    for k in range(3):
        y = top + (base - top) * k / 2
        parts.append(f'<line class="rule" x1="0" x2="{w}" y1="{y:.0f}" y2="{y:.0f}"/>')
    parts.append(f'<path class="area" d="{d} L{pts[-1][0]:.1f},{base} L{pts[0][0]:.1f},{base} Z"/>')
    parts.append(f'<path class="line" pathLength="1" d="{d}"/>')
    lx, ly = pts[-1]
    parts.append(f'<circle class="pt" cx="{lx-3:.1f}" cy="{ly:.1f}" r="3.5"/><circle class="halo" cx="{lx-3:.1f}" cy="{ly:.1f}" r="3.5"/>')
    shown = [i for i, l in enumerate(labels) if l]
    for j, i in enumerate(shown):
        if j % 2 == 0 and 16 < pts[i][0] < w - 16:
            parts.append(f'<text class="m" x="{pts[i][0]:.1f}" y="{h-8}" text-anchor="middle">{labels[i]}</text>')
    return svg(w, h, "".join(parts), "Contributions GitHub par semaine sur 12 mois")


def main():
    u = demo() if "--demo" in sys.argv else fetch(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("stats-langages", languages), ("stats-contributions", contributions)):
        with open(f"{OUT}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(fn(u))
    print("Graphiques générés dans", OUT)


if __name__ == "__main__":
    main()
