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




sys.path.insert(0, os.path.dirname(__file__))
from theme import write_pair  # noqa: E402

# ───────────── carte « Activité GitHub » (variante claire et sombre) ─────────────
PAL_L = ["#2F5BEA", "#0E9F8F", "#7C3AED", "#D97706", "#DB2777", "#0284C7"]
PAL_D = ["#7C9CFF", "#3CCFBE", "#A78BFA", "#FBBF24", "#F472B6", "#38BDF8"]

CSS = (":root{--card:#FFFFFF;--line:#E3E8F2;--ink:#111A33;--body:#3E4866;--muted:#6B7592;--faint:#E6EAF3;--track:#EEF1F7;--acc:#2F5BEA;--acc2:#0E9F8F;"
       + "".join(f"--l{i}:{c};" for i, c in enumerate(PAL_L)) + "}"
       "@media (prefers-color-scheme:dark){:root{--card:#10162A;--line:#242C44;--ink:#EEF2FB;--body:#B9C1D8;--muted:#8A94AF;--faint:#222A42;--track:#1A2238;--acc:#7C9CFF;--acc2:#3CCFBE;"
       + "".join(f"--l{i}:{c};" for i, c in enumerate(PAL_D)) + "}}"
       f".card{{fill:var(--card);stroke:var(--line)}}"
       f".h2{{fill:var(--ink);font:650 22px {FONT};letter-spacing:-.2px}}"
       f".sub{{fill:var(--muted);font:400 14px {FONT}}}"
       f".kpi{{fill:var(--ink);font:700 30px {FONT};letter-spacing:-.6px;font-variant-numeric:tabular-nums}}"
       f".kl{{fill:var(--muted);font:400 13px {FONT}}}"
       f".ax{{fill:var(--muted);font:400 12px {FONT}}}"
       f".lg{{fill:var(--body);font:500 13.5px {FONT}}}"
       f".lp{{fill:var(--muted);font:400 13px {FONT};font-variant-numeric:tabular-nums}}"
       f".tag{{fill:var(--ink);font:600 12.5px {FONT}}}"
       ".col{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:up .7s cubic-bezier(.2,.7,.2,1) forwards}"
       ".seg{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:gx .7s cubic-bezier(.3,0,.2,1) forwards}"
       ".in{opacity:0;animation:in .7s ease-out forwards}"
       "@keyframes up{to{transform:scaleY(1)}}@keyframes gx{to{transform:scaleX(1)}}@keyframes in{to{opacity:1}}"
       "@media (prefers-reduced-motion:reduce){*{animation:none!important;transform:none!important;opacity:1!important}}")


def lang_share(u):
    tot = OrderedDict()
    for r in u["repositories"]["nodes"]:
        for ed in r["languages"]["edges"]:
            tot[ed["node"]["name"]] = tot.get(ed["node"]["name"], 0) + ed["size"]
    items = sorted(tot.items(), key=lambda x: -x[1])
    s = sum(v for _, v in items) or 1
    top = [(n, v / s * 100) for n, v in items[:5]]
    rest = 100 - sum(p for _, p in top)
    if rest >= 0.5:
        top.append(("Autres", rest))
    return top


def activity(u):
    W, H = 1200, 470
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for wk in cal["weeks"] for d in wk["contributionDays"]]
    weeks, months, last = [], [], None
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append(sum(d["contributionCount"] for d in chunk))
        m = dt.date.fromisoformat(chunk[0]["date"]).month
        months.append(MOIS[m - 1] if m != last else "")
        last = m
    weeks, months = weeks[-52:], months[-52:]
    active = sum(1 for w in weeks if w)
    mx = max(weeks) or 1
    total = cal["totalContributions"]
    repos = u["repositories"]["totalCount"]

    b = [f'<rect class="card" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18"/>',
         f'<text class="h2" x="44" y="62">Activité GitHub</text>',
         f'<text class="sub" x="44" y="88">Contributions par semaine sur les 12 derniers mois</text>']
    kpis = [(str(total), "contributions"), (str(repos), "dépôts"), (f"{active}/{len(weeks)}", "semaines actives")]
    x = W - 44
    for i, (v, l) in enumerate(reversed(kpis)):
        b.append(f'<g class="in" style="animation-delay:{.1 + i*.1:.1f}s"><text class="kpi" x="{x}" y="66" text-anchor="end">{v}</text>'
                 f'<text class="kl" x="{x}" y="88" text-anchor="end">{e(l)}</text></g>')
        x -= max(len(v) * 18, len(l) * 7.2) + 44

    # histogramme hebdomadaire
    x0, x1, top, base = 44, W - 44, 136, 286
    for k in range(3):
        y = top + (base - top) * k / 2
        b.append(f'<line x1="{x0}" x2="{x1}" y1="{y:.0f}" y2="{y:.0f}" stroke="var(--faint)" stroke-dasharray="{"0" if k == 2 else "3 5"}"/>')
    n = len(weeks)
    step = (x1 - x0) / n
    bw = step * .62
    imax = weeks.index(mx)
    for i, v in enumerate(weeks):
        cx = x0 + step * i + (step - bw) / 2
        if v == 0:
            b.append(f'<rect x="{cx:.1f}" y="{base-3}" width="{bw:.1f}" height="3" rx="1.5" fill="var(--faint)"/>')
            continue
        h = max(4, (base - top) * v / mx)
        col = "var(--acc2)" if i == imax else "var(--acc)"
        op = 1 if i == imax else .35 + .65 * v / mx
        b.append(f'<rect class="col" style="animation-delay:{.2 + i*.018:.3f}s" x="{cx:.1f}" y="{base-h:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="{min(3, bw/2):.1f}" fill="{col}" fill-opacity="{op:.2f}"/>')
    px = x0 + step * imax + step / 2
    b.append(f'<g class="in" style="animation-delay:1.3s"><text class="tag" x="{min(max(px, 80), W-80):.1f}" y="{top-12}" text-anchor="middle">pic : {mx} contributions</text></g>')
    for i, m in enumerate(months):
        if m:
            b.append(f'<text class="ax" x="{x0 + step*i + step/2:.1f}" y="{base+24}" text-anchor="middle">{m}</text>')

    # langages : barre empilée + légende
    b.append(f'<line x1="44" x2="{W-44}" y1="338" y2="338" stroke="var(--line)"/>')
    b.append(f'<text class="h2" style="font-size:17px" x="44" y="378">Langages</text>')
    langs = lang_share(u)
    lx0, lx1, ly = 170, W - 44, 366
    b.append(f'<rect x="{lx0}" y="{ly}" width="{lx1-lx0}" height="12" rx="6" fill="var(--track)"/>')
    b.append(f'<clipPath id="lc"><rect x="{lx0}" y="{ly}" width="{lx1-lx0}" height="12" rx="6"/></clipPath><g clip-path="url(#lc)">')
    x = lx0
    for i, (name, p) in enumerate(langs):
        w = (lx1 - lx0) * p / 100
        b.append(f'<rect class="seg" style="animation-delay:{.4 + i*.15:.2f}s" x="{x:.1f}" y="{ly}" width="{w + .6:.1f}" height="12" fill="var(--l{i})"/>')
        x += w
    b.append('</g>')
    tw = lambda t, k: sum((k * 1.18 if c.isupper() else k) for c in t)
    x = lx0
    for i, (name, p) in enumerate(langs):
        label = f"{p:.0f} %"
        nw = tw(name, 7.4)
        b.append(f'<g class="in" style="animation-delay:{.6 + i*.12:.2f}s"><circle cx="{x+5}" cy="414" r="5" fill="var(--l{i})"/>'
                 f'<text class="lg" x="{x+16}" y="419">{e(name)}</text>'
                 f'<text class="lp" x="{x + 22 + nw:.0f}" y="419">{label}</text></g>')
        x += 22 + nw + len(label) * 7.4 + 30
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Activité GitHub : {total} contributions sur 12 mois, {repos} dépôts"><style>{CSS}</style>{"".join(b)}</svg>')


def main():
    u = demo() if "--demo" in sys.argv else fetch(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    os.makedirs(OUT, exist_ok=True)
    write_pair(OUT, "activite.svg", activity(u))
    print("Graphiques générés dans", OUT)


if __name__ == "__main__":
    main()
