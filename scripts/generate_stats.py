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


def stars(w, h, n=40):
    import random
    rnd = random.Random(w * 7 + h)
    return "".join(
        f'<circle cx="{rnd.uniform(8, w-8):.0f}" cy="{rnd.uniform(8, h-8):.0f}" r="{rnd.uniform(.3, 1.1):.2f}" fill="#F2F4FF" '
        f'class="tw" style="animation-delay:-{rnd.uniform(0, 4):.1f}s"/>' for _ in range(n))


def card(w, h, body, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><radialGradient id="g" cx=".5" cy=".2" r=".9"><stop offset="0" stop-color="#0A0E22"/><stop offset="1" stop-color="#03040A"/></radialGradient>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{LIGHT}"/></linearGradient>
<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{ACC}"/><stop offset="1" stop-color="{LIGHT}"/></linearGradient></defs>
<style>.c{{animation:in .8s ease-out both}}@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.grow{{transform-box:fill-box;transform-origin:bottom;animation:gr 1s ease-out both}}@keyframes gr{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
.tw{{animation:tw 4s ease-in-out infinite}}@keyframes tw{{0%,100%{{opacity:.2}}50%{{opacity:.9}}}}
.wide{{transform-box:fill-box;transform-origin:left;animation:wd 1s ease-out both}}@keyframes wd{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}</style>
<g class="c"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="22" fill="url(#g)" stroke="#1C2246"/>
{stars(w, h)}
<text x="28" y="44" font-family="{FONT}" font-size="18" font-weight="700" fill="{TXT}">{e(title)}</text>
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
    return card(w, h, "".join(parts), "En chiffres")


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
    return card(w, h, "".join(parts), "Langages les plus utilisés")


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
    parts = [f'<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="#1C2246"/>']
    for i, ((yy, m), v) in enumerate(counts.items()):
        x = left + i * step + (step - bw) / 2
        bh = (base - top_) * v / mx
        if v:
            parts.append(f'<rect class="grow" style="animation-delay:{i*0.06:.2f}s" x="{x:.1f}" y="{base-bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="url(#bar)"/>'
                         f'<text x="{x+bw/2:.1f}" y="{base-bh-6:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TXT}">{v}</text>')
        parts.append(f'<text x="{x+bw/2:.1f}" y="{base+20}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">{MOIS[m-1]}</text>')
    return card(w, h, "".join(parts), "Activité mensuelle")


# ─────────────── courbes (contributions hebdo + visites du profil) ───────────────
VIEWS_URL = "https://komarev.com/ghpvc/?username={user}&abbreviated=false"
HISTORY_URL = "https://raw.githubusercontent.com/{repo}/stats/views-history.json"
GREEN = "#5BE49B"


def smooth(pts, lo=None, hi=None):
    """Courbe lisse (Catmull-Rom → Bézier) passant par tous les points."""
    if len(pts) < 2:
        return ""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if hi is not None:  # pas de dépassement sous l'axe
            c1 = (c1[0], min(max(c1[1], lo), hi)); c2 = (c2[0], min(max(c2[1], lo), hi))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


CURVE_CSS = (".draw{stroke-dasharray:1;stroke-dashoffset:1;animation:dw 2.6s cubic-bezier(.4,0,.2,1) .3s forwards}"
             "@keyframes dw{to{stroke-dashoffset:0}}"
             ".area{opacity:0;animation:ar 1.6s ease-out 1.6s forwards}@keyframes ar{to{opacity:1}}"
             ".pulse{animation:pu 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}"
             "@keyframes pu{0%{transform:scale(1);opacity:.8}100%{transform:scale(3.4);opacity:0}}")


def curve_card(w, h, title, values, labels, color, color2, big, small, empty_msg=None):
    left, right, top, base = 28, w - 28, 112, h - 44
    parts = [f'<text x="{w-28}" y="44" text-anchor="end" font-family="{FONT}" font-size="30" font-weight="800" fill="#FFFFFF">{e(big)}</text>'
             f'<text x="{w-28}" y="68" text-anchor="end" font-family="{FONT}" font-size="13" fill="{MUTED}">{e(small)}</text>']
    for k in range(4):  # grille discrète
        y = top + (base - top) * k / 3
        parts.append(f'<line x1="{left}" y1="{y:.0f}" x2="{right}" y2="{y:.0f}" stroke="#FFFFFF" stroke-opacity=".05"/>')
    if len(values) < 2:
        parts.append(f'<text x="{w/2}" y="{(top+base)/2+6:.0f}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="{MUTED}">{e(empty_msg or "")}</text>')
        return curve_wrap(w, h, title, "".join(parts), color, color2)
    mx = max(values) or 1
    n = len(values)
    pts = [(left + (right - left) * i / (n - 1), base - (base - top) * v / mx) for i, v in enumerate(values)]
    d = smooth(pts, top - 8, base)
    area = d + f" L{pts[-1][0]:.1f},{base} L{pts[0][0]:.1f},{base} Z"
    parts.append(f'<path class="area" d="{area}" fill="url(#ag)"/>')
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="6" stroke-opacity=".18" stroke-linecap="round" filter="url(#bl)"/>')
    parts.append(f'<path class="draw" pathLength="1" d="{d}" fill="none" stroke="url(#lg)" stroke-width="2.4" stroke-linecap="round"/>')
    # point lumineux qui parcourt la courbe
    parts.append(f'<circle r="4" fill="#fff"><animateMotion dur="6s" begin="3s" repeatCount="indefinite" path="{d}"/></circle>')
    # pic
    im = values.index(mx)
    px, py = pts[im]
    parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color2}"/><circle class="pulse" cx="{px:.1f}" cy="{py:.1f}" r="4" fill="none" stroke="{color2}" stroke-width="1.5"/>'
                 f'<text x="{min(max(px, 60), w-60):.1f}" y="{py-14:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{TXT}">pic : {mx}</text>')
    # dernier point
    lx, ly = pts[-1]
    parts.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="{GREEN}"/><circle class="pulse" cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="none" stroke="{GREEN}" stroke-width="1.5"/>')
    # étiquettes de l'axe
    step = max(1, n // 8)
    sparse = sum(1 for l in labels if l) <= 14
    for i in range(n):
        if labels[i] and (sparse or i % step == 0):
            parts.append(f'<text x="{pts[i][0]:.1f}" y="{base+24}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{MUTED}">{e(labels[i])}</text>')
    return curve_wrap(w, h, title, "".join(parts), color, color2)


def curve_wrap(w, h, title, body, color, color2):
    extra = (f'<linearGradient id="lg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color2}"/></linearGradient>'
             f'<linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".35"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>'
             '<filter id="bl" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>')
    svg = card(w, h, body, title)
    return svg.replace("</defs>", extra + "</defs>", 1).replace("</style>", CURVE_CSS + "</style>", 1)


def contributions_curve(u):
    days = [d for wk in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in wk["contributionDays"]]
    weeks, labels, last_month = [], [], None
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append(sum(d["contributionCount"] for d in chunk))
        m = dt.date.fromisoformat(chunk[0]["date"]).month
        labels.append(MOIS[m - 1] if m != last_month else "")
        last_month = m
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    return curve_card(1200, 330, "Contributions par semaine", weeks, labels, ACC, "#C9A6FF",
                      str(total), "contributions sur 12 mois")


def load_history(repo):
    try:
        with urllib.request.urlopen(HISTORY_URL.format(repo=repo), timeout=15) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


def fetch_views(user):
    import re
    req = urllib.request.Request(VIEWS_URL.format(user=user), headers={"User-Agent": "profile-stats"})
    with urllib.request.urlopen(req, timeout=15) as r:
        txt = r.read().decode()
    nums = re.findall(r">\s*([\d,\. ]+)\s*<", txt)
    nums = [int(re.sub(r"\D", "", n)) for n in nums if re.sub(r"\D", "", n)]
    return max(nums) if nums else None


def views_curve(hist):
    dates = sorted(hist)
    daily, labels = [], []
    for a, b in zip(dates, dates[1:]):
        daily.append(max(0, hist[b] - hist[a] - 1))  # -1 : la visite du robot lui-même
        dd = dt.date.fromisoformat(b)
        labels.append(f"{dd.day} {MOIS[dd.month-1]}")
    total = hist[dates[-1]] if dates else 0
    start = dt.date.fromisoformat(dates[0]) if dates else dt.date.today()
    msg = f"Suivi démarré le {start.day} {MOIS[start.month-1]} {start.year} · la courbe se dessine jour après jour"
    return curve_card(1200, 330, "Visites du profil par jour", daily[-60:], labels[-60:], "#7FE3FF", ACC,
                      str(total), "visites au total", empty_msg=msg)


def update_views(user, repo):
    hist = load_history(repo)
    try:
        v = fetch_views(user)
        if v is not None:
            hist[dt.date.today().isoformat()] = v
    except Exception as ex:
        print("Compteur de visites indisponible :", ex)
    with open(f"{OUT}/views-history.json", "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=0, sort_keys=True)
    return hist


def main():
    if "--demo" in sys.argv:
        u = demo()
    else:
        u = fetch(os.environ["GH_USER"], os.environ["GITHUB_TOKEN"])
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("stats-chiffres", kpis), ("stats-langages", languages), ("stats-activite", activity),
                     ("stats-courbe", contributions_curve)):
        with open(f"{OUT}/{name}.svg", "w", encoding="utf-8") as f:
            f.write(fn(u))
    if "--demo" in sys.argv:
        hist = {(dt.date.today() - dt.timedelta(days=30 - i)).isoformat(): 40 + i * 3 + (i * 7) % 11 for i in range(31)}
    else:
        hist = update_views(os.environ["GH_USER"], os.environ.get("GITHUB_REPOSITORY", "adam-hassen/adam-hassen"))
    with open(f"{OUT}/stats-visites.svg", "w", encoding="utf-8") as f:
        f.write(views_curve(hist))
    print("Graphiques générés dans", OUT)


if __name__ == "__main__":
    main()
