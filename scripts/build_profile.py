"""Génère les visuels du profil GitHub dans assets/.

Bannière, parcours (expérience et formation) et cartes de projets.
Fonds de carte et couleurs suivent le thème clair ou sombre de GitHub.
Usage : python scripts/build_profile.py
"""
import html
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
e = html.escape

TOKENS = """
:root{--card:#FFFFFF;--line:#E3E8F2;--ink:#111A33;--body:#3E4866;--muted:#6B7592;--chip:#F2F5FB;
--acc:#2F5BEA;--acc2:#0E9F8F;--ok:#12A150;--wash1:#E9EEFF;--wash2:#E3F6F3}
@media (prefers-color-scheme:dark){:root{--card:#10162A;--line:#242C44;--ink:#EEF2FB;--body:#B9C1D8;
--muted:#8A94AF;--chip:#18203A;--acc:#7C9CFF;--acc2:#3CCFBE;--ok:#3DDC84;--wash1:#18224A;--wash2:#0F2A2E}}
"""

BASE = f"""
.card{{fill:var(--card);stroke:var(--line);stroke-width:1}}
.h1{{fill:var(--ink);font:700 56px {SANS};letter-spacing:-1.4px}}
.h2{{fill:var(--ink);font:650 22px {SANS};letter-spacing:-.2px}}
.h3{{fill:var(--ink);font:650 18px {SANS}}}
.role{{fill:var(--acc);font:600 21px {SANS}}}
.body{{fill:var(--body);font:400 15px {SANS}}}
.small{{fill:var(--muted);font:400 13px {SANS}}}
.date{{fill:var(--muted);font:500 13px {SANS};font-variant-numeric:tabular-nums}}
.kick{{font:600 12.5px {SANS}}}
.chip{{fill:var(--chip)}}
.chipt{{fill:var(--body);font:500 12.5px {SANS}}}
.acc{{fill:var(--acc)}}.acc2{{fill:var(--acc2)}}
.in{{opacity:0;animation:in .8s cubic-bezier(.2,.7,.2,1) forwards}}
@keyframes in{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes show{{to{{opacity:1}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes grow{{to{{transform:scaleX(1)}}}}
@keyframes pulse{{0%{{transform:scale(1);opacity:.8}}100%{{transform:scale(3.2);opacity:0}}}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 2.2s ease-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;stroke-dashoffset:0!important;transform:none!important}}.pulse{{opacity:0!important}}}}
"""


def svg(w, h, body, label, css="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><defs>{defs}</defs><style>{TOKENS}{BASE}{css}</style>{body}</svg>')


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)


def text_w(s, size):
    return len(s) * size * 0.56


def chips(x, y, items, delay=0.0):
    out = []
    for i, t in enumerate(items):
        w = text_w(t, 12.5) + 22
        out.append(f'<g class="in" style="animation-delay:{delay + i*.06:.2f}s"><rect class="chip" x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13"/>'
                   f'<text class="chipt" x="{x + 11:.0f}" y="{y + 17.5}">{e(t)}</text></g>')
        x += w + 8
    return "".join(out)


def wrap(t, n):
    words, lines, cur = t.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def smooth(pts):
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


# ─────────────────────────────── BANNIÈRE ───────────────────────────────
def header():
    W, H = 1200, 340
    gx0, gx1, gy0, gy1 = 730, 1140, 92, 250
    rnd = random.Random(11)
    v, vals = 0.0, []
    for i in range(60):
        v += rnd.gauss(0.08, 0.5)
        vals.append(v + 1.5 * math.sin(i / 6.5))
    k = 44
    hist = vals[:k]
    slope = (hist[-1] - hist[-10]) / 9
    nf = len(vals) - k + 1
    fc = [hist[-1] + slope * i * .85 for i in range(nf)]
    band = [.3 + .26 * i for i in range(nf)]
    lo = min(min(hist), min(a - b for a, b in zip(fc, band))) - .8
    hi = max(max(hist), max(a + b for a, b in zip(fc, band))) + .8
    n = len(vals)
    P = lambda arr, s: [(gx0 + (gx1 - gx0) * (s + i) / (n - 1), gy1 - (gy1 - gy0) * (a - lo) / (hi - lo)) for i, a in enumerate(arr)]
    ph, pf = P(hist, 0), P(fc, k - 1)
    up, dn = P([a + b for a, b in zip(fc, band)], k - 1), P([a - b for a, b in zip(fc, band)], k - 1)
    dh, df = smooth(ph), smooth(pf)
    dband = smooth(up) + " L" + smooth(list(reversed(dn)))[1:] + " Z"
    area = dh + f" L{ph[-1][0]:.1f},{gy1} L{ph[0][0]:.1f},{gy1} Z"
    sx, sy = ph[-1]
    ex, ey = pf[-1]
    # quelques points de mesure sur l'historique
    marks = "".join(f'<circle cx="{ph[i][0]:.1f}" cy="{ph[i][1]:.1f}" r="2.6" class="acc" style="opacity:0;animation:show .3s ease-out {0.4 + 2.2*i/k:.2f}s forwards"/>'
                    for i in range(4, k, 8))
    grid = "".join(f'<line x1="{gx0}" x2="{gx1}" y1="{gy0 + (gy1-gy0)*i/3:.0f}" y2="{gy0 + (gy1-gy0)*i/3:.0f}" stroke="var(--line)"/>' for i in range(4))

    facts = [("loc", "Le Mans, France"), ("cal", "Disponible en mars 2027"), ("lang", "Français, anglais, arabe")]
    icons = {
        "loc": '<path d="M0-7a5 5 0 0 1 5 5c0 4-5 9-5 9s-5-5-5-9a5 5 0 0 1 5-5z" fill="none" stroke="var(--muted)" stroke-width="1.5"/><circle cy="-2" r="1.7" fill="var(--muted)"/>',
        "cal": '<circle r="4" fill="var(--ok)"/><circle class="pulse" r="4" fill="none" stroke="var(--ok)" stroke-width="1.5"/>',
        "lang": '<circle r="6.5" fill="none" stroke="var(--muted)" stroke-width="1.5"/><path d="M-6.5 0h13M0-6.5c3 3.5 3 9.5 0 13M0-6.5c-3 3.5-3 9.5 0 13" fill="none" stroke="var(--muted)" stroke-width="1.2"/>',
    }
    fx, frow = 56, []
    for i, (ic, t) in enumerate(facts):
        frow.append(f'<g class="in" style="animation-delay:{.7 + i*.1:.1f}s"><g transform="translate({fx+7} 285)">{icons[ic]}</g>'
                    f'<text class="small" x="{fx+22}" y="290" style="fill:var(--body)">{e(t)}</text></g>')
        fx += text_w(t, 13) + 60

    defs = ('<linearGradient id="wash" x1="0" y1="0" x2="1" y2="0"><stop offset=".45" stop-color="var(--card)" stop-opacity="0"/>'
            '<stop offset="1" stop-color="var(--wash1)"/></linearGradient>'
            '<radialGradient id="wash2" cx="1" cy="1" r=".7"><stop offset="0" stop-color="var(--wash2)"/><stop offset="1" stop-color="var(--wash2)" stop-opacity="0"/></radialGradient>'
            '<linearGradient id="stroke" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="var(--acc)" stop-opacity=".35"/><stop offset="1" stop-color="var(--acc)"/></linearGradient>'
            '<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--acc)" stop-opacity=".18"/><stop offset="1" stop-color="var(--acc)" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="cc"><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18"/></clipPath>')
    css = (".hist{fill:none;stroke:url(#stroke);stroke-width:2.4;stroke-linecap:round;stroke-dasharray:1;stroke-dashoffset:1;"
           "animation:draw 2.4s cubic-bezier(.45,0,.2,1) .3s forwards}"
           ".area{opacity:0;animation:show 1s ease-out 2.3s forwards}"
           ".fc{fill:none;stroke:var(--acc2);stroke-width:2.2;stroke-dasharray:5 6;opacity:0;animation:show .8s ease-out 2.6s forwards}"
           ".band{fill:var(--acc2);opacity:0;animation:band 1.2s ease-out 2.7s forwards}@keyframes band{to{opacity:.13}}"
           ".now{stroke:var(--muted);stroke-dasharray:2 4;opacity:0;animation:show .6s ease-out 2.4s forwards}"
           ".late{opacity:0;animation:show .5s ease-out 3.1s forwards}")
    body = [f'<rect class="card" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18"/>',
            '<g clip-path="url(#cc)">',
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#wash)"/>',
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#wash2)"/>',
            '</g>',
            f'<text class="h1 in" x="54" y="118">Adam Hassen</text>',
            f'<text class="role in" style="animation-delay:.15s" x="56" y="160">Data Scientist et ingénieur IHM en formation</text>',
            f'<text class="body in" style="animation-delay:.3s;font-size:16.5px" x="56" y="204">Double diplôme d\'ingénieur ESPRIT et ENSIM, Le Mans Université.</text>',
            f'<text class="body in" style="animation-delay:.4s;font-size:16.5px" x="56" y="230">Je cherche un stage de fin d\'études de 6 mois en Data et IA.</text>',
            f'<line x1="56" x2="660" y1="256" y2="256" stroke="var(--line)" class="in" style="animation-delay:.6s"/>',
            "".join(frow),
            grid,
            f'<path class="area" d="{area}" fill="url(#fill)"/>',
            f'<path class="band" d="{dband}"/>',
            f'<line class="now" x1="{sx:.1f}" x2="{sx:.1f}" y1="{gy0-18}" y2="{gy1}"/>',
            f'<path class="hist" pathLength="1" d="{dh}"/>',
            marks,
            f'<path class="fc" d="{df}"/>',
            f'<g class="late"><circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="var(--acc2)"/></g>',
            f'<circle class="pulse late" cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="none" stroke="var(--acc2)" stroke-width="1.5" style="animation:pulse 2.2s ease-out 3.3s infinite"/>',
            f'<text class="small in" style="animation-delay:2.5s" x="{sx-10:.1f}" y="{gy0-24}" text-anchor="end">historique</text>',
            f'<text class="small in" style="animation-delay:2.8s;fill:var(--acc2)" x="{sx+10:.1f}" y="{gy0-24}">prévision</text>']
    write("header.svg", svg(W, H, "".join(body), "Adam Hassen, Data Scientist et ingénieur IHM en formation. Stage de fin d'études de 6 mois en Data et IA, disponible en mars 2027.", css, defs))


# ─────────────────────────────── PARCOURS ───────────────────────────────
def parcours():
    W = 1200
    exp = [
        ("2025 – 2026", "Associé technique", "LinqCe",
         "Cofondation d'une plateforme de mise en relation entre indépendants, entreprises, associations et administrations. Intégration de l'IA et développement full-stack."),
        ("2024 – 2025", "Stage ingénieur", "Vermeg, département Assurance",
         "Dashboard de surveillance des logs en temps réel, classification automatique des erreurs et modèle prédictif pour anticiper les incidents."),
        ("2023 – 2024", "Stage", "Aman Bank",
         "Application web bancaire en Angular et Node.js : authentification, modules, consultation des chèques et des effets."),
    ]
    edu = [
        ("2025 – 2027", "Ingénieur informatique, IHM", "ENSIM, Le Mans Université",
         "Spécialité Interaction Personnes-Systèmes : UX/UI, DevOps, mobile, visualisation, réalité augmentée, ML avancé."),
        ("2021 – 2026", "Ingénieur informatique, Data Science", "ESPRIT, Tunis",
         "Statistiques, séries temporelles, Big Data, machine learning et deep learning."),
    ]

    def column(x0, title, items, color, delay0, wrapn):
        out = [f'<text class="h2 in" style="animation-delay:{delay0:.2f}s" x="{x0}" y="62">{e(title)}</text>']
        y = 112
        tops = []
        for i, (date, role, org, desc) in enumerate(items):
            d = delay0 + .25 + i * .22
            lines = wrap(desc, wrapn)
            tops.append(y)
            out.append(f'<g class="in" style="animation-delay:{d:.2f}s">'
                       f'<circle cx="{x0+6}" cy="{y-5}" r="6" fill="var(--card)" stroke="{color}" stroke-width="2"/>'
                       f'<circle cx="{x0+6}" cy="{y-5}" r="2.5" fill="{color}"/>'
                       f'<text class="date" x="{x0+28}" y="{y}">{e(date)}</text>'
                       f'<text class="h3" x="{x0+28}" y="{y+28}">{e(role)}</text>'
                       f'<text class="kick" x="{x0+28}" y="{y+50}" style="fill:{color}">{e(org)}</text>'
                       + "".join(f'<text class="body" x="{x0+28}" y="{y+76 + j*22}">{e(l)}</text>' for j, l in enumerate(lines))
                       + '</g>')
            y += 76 + len(lines) * 22 + 34
        last = tops[-1] - 5
        out.insert(1, f'<line x1="{x0+6}" x2="{x0+6}" y1="{tops[0]-5}" y2="{last}" stroke="var(--line)" stroke-width="2"/>'
                      f'<line class="rail" pathLength="1" x1="{x0+6}" x2="{x0+6}" y1="{tops[0]-5}" y2="{last}" stroke="{color}" stroke-width="2" '
                      f'style="animation-delay:{delay0+.2:.2f}s"/>')
        return "".join(out), y

    left, hl = column(48, "Expérience", exp, "var(--acc)", 0, 64)
    right, hr = column(664, "Formation", edu, "var(--acc2)", .3, 58)
    H = int(max(hl, hr)) - 4
    css = ".rail{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.6s cubic-bezier(.45,0,.2,1) forwards}"
    body = (f'<rect class="card" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18"/>'
            f'<line x1="620" x2="620" y1="40" y2="{H-40}" stroke="var(--line)"/>' + left + right)
    write("parcours.svg", svg(W, H, body, "Expérience : LinqCe, Vermeg, Aman Bank. Formation : ENSIM et ESPRIT.", css))


# ─────────────────────────────── PROJETS ───────────────────────────────
def motif(kind, x, y):
    """Petit pictogramme animé, propre à chaque type de projet (zone 120×80)."""
    if kind == "ia":  # réseau de nœuds
        nodes = [(0, 20), (0, 60), (50, 8), (50, 40), (50, 72), (100, 40)]
        edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)]
        s = "".join(f'<line x1="{x+nodes[a][0]}" y1="{y+nodes[a][1]}" x2="{x+nodes[b][0]}" y2="{y+nodes[b][1]}" stroke="var(--k)" stroke-opacity=".35" '
                    f'class="edge" pathLength="1" style="animation-delay:{.3+i*.05:.2f}s"/>' for i, (a, b) in enumerate(edges))
        s += "".join(f'<circle cx="{x+a}" cy="{y+b}" r="5" fill="var(--card)" stroke="var(--k)" stroke-width="2"/>' for a, b in nodes)
        s += f'<circle cx="{x+100}" cy="{y+40}" r="2.5" fill="var(--k)" class="blink"/>'
        return s
    if kind == "data":  # barres
        hs = [26, 44, 34, 58, 48, 70]
        return "".join(f'<rect x="{x+i*18}" y="{y+80-h}" width="11" height="{h}" rx="3" fill="var(--k)" fill-opacity="{.35 + i*.11:.2f}" '
                       f'class="bar" style="animation-delay:{.3+i*.08:.2f}s"/>' for i, h in enumerate(hs))
    if kind == "signal":  # onde
        pts = [(x + i * 2, y + 40 + 18 * math.sin(i / 3.2) * math.exp(-((i - 30) / 22) ** 2) + 4 * math.sin(i * 1.7)) for i in range(61)]
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        return f'<path d="{d}" fill="none" stroke="var(--k)" stroke-width="2" stroke-linejoin="round" class="edge" pathLength="1" style="animation-duration:1.8s"/>'
    if kind == "jeu":  # cube
        c = f'translate({x+60} {y+40})'
        return (f'<g transform="{c}"><g class="spin">'
                '<path d="M0-30L26-15V15L0 30-26 15V-15Z" fill="none" stroke="var(--k)" stroke-width="2"/>'
                '<path d="M-26-15L0 0 26-15M0 0V30" fill="none" stroke="var(--k)" stroke-width="2" stroke-opacity=".5"/></g></g>')
    if kind == "ar":  # viseur
        return (f'<g transform="translate({x+60} {y+40})">'
                '<path d="M-34-20v-14h14M20-34h14v14M34 20v14H20M-20 34h-14V20" fill="none" stroke="var(--k)" stroke-width="2.2" stroke-linecap="round"/>'
                '<circle r="9" fill="none" stroke="var(--k)" stroke-width="2"/><circle r="9" fill="none" stroke="var(--k)" class="pulse"/></g>')
    if kind == "mobile":  # téléphone
        return (f'<g transform="translate({x+42} {y})"><rect width="38" height="80" rx="8" fill="none" stroke="var(--k)" stroke-width="2"/>'
                '<rect x="7" y="40" width="24" height="5" rx="2.5" fill="var(--k)" fill-opacity=".3"/>'
                '<rect x="7" y="40" width="24" height="5" rx="2.5" fill="var(--k)" class="bar2"/>'
                '<rect x="7" y="52" width="16" height="4" rx="2" fill="var(--k)" fill-opacity=".3"/><rect x="7" y="61" width="20" height="4" rx="2" fill="var(--k)" fill-opacity=".3"/>'
                '<circle cx="19" cy="22" r="9" fill="none" stroke="var(--k)" stroke-width="2" stroke-opacity=".5"/></g>')
    return ""


def project(fname, kind, color, kicker, title, desc, tech):
    W, H = 590, 236
    lines = wrap(desc, 50)
    light, dark = color if isinstance(color, tuple) else (color, color)
    color = "var(--k)"
    css = (f":root{{--k:{light}}}@media (prefers-color-scheme:dark){{:root{{--k:{dark}}}}}"
           ".edge{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1s ease-out forwards}"
           ".bar{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:up .9s cubic-bezier(.2,.7,.2,1) forwards}"
           "@keyframes up{to{transform:scaleY(1)}}"
           ".blink{animation:bk 1.6s ease-in-out infinite}@keyframes bk{50%{opacity:.2}}"
           ".spin{animation:sp 9s linear infinite;transform-box:fill-box;transform-origin:center}@keyframes sp{to{transform:rotate(360deg)}}"
           ".bar2{transform-box:fill-box;transform-origin:left;animation:fill 2.6s ease-in-out infinite}@keyframes fill{0%{transform:scaleX(0)}70%,100%{transform:scaleX(1)}}"
           ".top{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1s cubic-bezier(.3,0,.2,1) .1s forwards}"
           ".arrow{opacity:.55}")
    body = [f'<rect class="card" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16"/>',
            f'<rect class="top" x="28" y="0.5" width="64" height="3" rx="1.5" fill="{color}"/>',
            f'<g class="in"><text class="kick" x="28" y="46" style="fill:{color}">{e(kicker)}</text>'
            f'<text class="h2" x="28" y="78">{e(title)}</text></g>',
            "".join(f'<text class="body in" style="animation-delay:.12s" x="28" y="{110 + j*22}">{e(l)}</text>' for j, l in enumerate(lines)),
            chips(28, H - 50, tech, .25),
            f'<g opacity=".95">{motif(kind, W - 152, 30)}</g>',
            f'<path class="arrow" d="M{W-40} {H-42}l8-8m0 0h-7m7 0v7" fill="none" stroke="var(--muted)" stroke-width="1.6" stroke-linecap="round"/>']
    write(fname, svg(W, H, "".join(body), f"{title} : {desc}", css))


PROJECTS = [
    ("projet-assuria.svg", "ia", ("#2F5BEA", "#7C9CFF"), "IA appliquée, en cours", "AssurIA",
     "Offres d'assurance personnalisées par un petit LLM, conseiller RAG sur les contrats et prédiction du coût des sinistres.",
     ["Python", "LLM", "RAG", "PostgreSQL"]),
    ("projet-stock.svg", "data", ("#0E9F8F", "#3CCFBE"), "Data engineering", "Stock Auto Update",
     "Pipeline automatisé qui collecte les données boursières, analyse le sentiment des actualités et publie le dataset sur Hugging Face.",
     ["Python", "FinBERT", "GitHub Actions"]),
    ("projet-eeg.svg", "signal", ("#C2410C", "#FB923C"), "Machine learning sur signaux", "Charge cognitive EEG",
     "Estimation de la charge cognitive d'un conducteur en simulation à partir de signaux EEG, sur le dataset CL-Drive.",
     ["Python", "EEG", "scikit-learn"]),
    ("projet-neuron.svg", "jeu", ("#7C3AED", "#A78BFA"), "Jeu pédagogique", "Neuron Forge",
     "Jeu à la première personne où l'on construit, entraîne et valide un réseau de neurones dans un laboratoire.",
     ["C++", "Unreal Engine 5"]),
    ("projet-ar.svg", "ar", ("#DB2777", "#F472B6"), "Réalité augmentée", "AR-Secours",
     "Application Android de réalité augmentée pour apprendre les gestes de premiers secours.",
     ["C#", "Unity", "AR Foundation"]),
    ("projet-budget.svg", "mobile", ("#0284C7", "#38BDF8"), "Application mobile", "MonBudget",
     "Application Android de gestion de budget pour étudiants : dépenses, objectifs et tableau de bord.",
     ["Kotlin", "Jetpack Compose", "Room"]),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    header()
    parcours()
    for p in PROJECTS:
        project(*p)
    print("Visuels générés dans", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
