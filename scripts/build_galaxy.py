"""Génère les visuels animés « galaxie » du profil GitHub (SVG, animations CSS + SMIL).

Usage : python scripts/build_galaxy.py   → écrit tout dans assets/
Les SVG sont affichés via <img> par GitHub : pas de JavaScript, mais CSS/SMIL animés OK.
"""
import base64
import html
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
SANS = "'Avenir Next','SF Pro Display',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"

# Palette « espace profond »
VOID = "#03040A"      # fond
NIGHT = "#0A0E22"     # nébuleuse sombre
INDIGO = "#6E7BFF"    # accent principal
VIOLET = "#A88BFF"    # accent secondaire
HALO = "#9DB4FF"      # lueur de l'horizon
STAR = "#F2F4FF"      # texte / étoiles
MUTED = "#8C93AE"     # texte secondaire
LINE = "#1C2246"      # traits discrets
GREEN = "#5BE49B"     # statut « disponible »

e = html.escape


def svg(w, h, body, style="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<defs>{defs}</defs><style>{BASE_CSS}{style}</style>{body}</svg>')


BASE_CSS = (
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    ".tw1{animation:tw 3.2s ease-in-out infinite}.tw2{animation:tw 4.7s ease-in-out infinite}"
    ".tw3{animation:tw 6.1s ease-in-out infinite}"
    "@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}"
    ".drift{animation:dr 60s ease-in-out infinite alternate}.drift2{animation:dr2 90s ease-in-out infinite alternate}"
    "@keyframes dr{to{transform:translate(-36px,6px)}}@keyframes dr2{to{transform:translate(24px,-8px)}}"
    ".shoot{opacity:0;animation:sh 9s linear infinite}"
    "@keyframes sh{0%{opacity:0;transform:translate(0,0)}2%{opacity:1}9%{opacity:0;transform:translate(-340px,170px)}100%{opacity:0;transform:translate(-340px,170px)}}"
)


def starfield(w, h, n, seed, size=(0.3, 1.5), avoid=None):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        if avoid and avoid(x, y):
            continue
        r = rnd.uniform(*size) * (1.8 if rnd.random() < 0.04 else 1)
        cls = rnd.choice(["tw1", "tw2", "tw3", "", ""])
        col = rnd.choice([STAR, STAR, STAR, "#C9D2FF", "#E4D9FF"])
        d = rnd.uniform(0, 6)
        st = f' style="animation-delay:-{d:.1f}s"' if cls else ""
        op = "" if cls else f' opacity="{rnd.uniform(.25,.8):.2f}"'
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" class="{cls}"{st}{op}/>')
    return "".join(out)


def shooting(points):
    """points : liste de (x, y, délai)."""
    out = []
    for x, y, d in points:
        out.append(f'<g class="shoot" style="animation-delay:{d}s"><line x1="{x}" y1="{y}" x2="{x+90}" y2="{y-45}" '
                   f'stroke="url(#comet)" stroke-width="1.6" stroke-linecap="round"/>'
                   f'<circle cx="{x}" cy="{y}" r="1.6" fill="#fff"/></g>')
    return "".join(out)


COMET = ('<linearGradient id="comet" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#fff"/>'
         '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')


def frame(w, h, rx=22):
    return (f'<rect width="{w}" height="{h}" rx="{rx}" fill="url(#bg)"/>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="{LINE}"/>')


def bg_defs(cx=0.5, cy=0.3):
    return (f'<radialGradient id="bg" cx="{cx}" cy="{cy}" r="0.9"><stop offset="0" stop-color="{NIGHT}"/>'
            f'<stop offset="1" stop-color="{VOID}"/></radialGradient>{COMET}')


def pill(x, y, text, font=SANS, size=14, pad=16, cw=None):
    cw = cw or size * 0.56
    w = len(text) * cw + pad * 2
    return (f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="{size+18}" rx="{(size+18)/2}" fill="#FFFFFF" fill-opacity=".03" stroke="#2A3160"/>'
            f'<text x="{x + w/2:.0f}" y="{y + size + 4}" text-anchor="middle" font-family="{font}" font-size="{size}" fill="#D7DCF5">{e(text)}</text>'), w


def pills_centered(cx, y, items, gap=12, size=15):
    widths = [len(t) * size * 0.56 + 32 for t in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = cx - total / 2
    out = []
    for t, w in zip(items, widths):
        out.append(pill(x, y, t, size=size)[0])
        x += w + gap
    return "".join(out)


# ─────────────────────────── HERO ───────────────────────────
def spiral(seed=7, arms=3, per=170, rmax=330):
    rnd = random.Random(seed)
    dots = []
    for a in range(arms):
        base = a * 2 * math.pi / arms
        for i in range(per):
            t = i / per
            r = 18 + t * rmax
            th = base + t * 4.2 + rnd.gauss(0, 0.16)
            rr = r + rnd.gauss(0, 7)
            x, y = rr * math.cos(th), rr * math.sin(th)
            size = max(0.5, 2.6 * (1 - t) + rnd.uniform(0, 1.0))
            col = rnd.choice([STAR, "#C9D2FF", INDIGO, VIOLET, "#FFD9F2"])
            op = 0.45 + 0.55 * (1 - t * .7) * rnd.uniform(.6, 1)
            cls = ' class="tw2"' if rnd.random() < .12 else ""
            dots.append(f'<path d="M{x:.1f} {y:.1f}h.01" stroke="{col}" stroke-width="{size*1.6:.2f}" opacity="{op:.2f}"{cls}/>')
    for _ in range(420):  # poussière diffuse
        r = abs(rnd.gauss(0, 120))
        th = rnd.uniform(0, 2 * math.pi)
        dots.append(f'<path d="M{r*math.cos(th):.1f} {r*math.sin(th):.1f}h.01" stroke="{STAR}" stroke-width="{rnd.uniform(.6,1.8):.2f}" opacity="{rnd.uniform(.15,.5):.2f}"/>')
    # points ronds quelle que soit l'inclinaison : trait de longueur nulle, extrémité ronde, épaisseur non mise à l'échelle
    return f'<g class="gx" stroke-linecap="round">{"".join(dots)}</g>'



def hero(avatar_b64):
    W, H = 1200, 600
    cx, cy = 600, 196
    roles = [
        "Élève ingénieur · double diplôme ESPRIT × ENSIM",
        "Data Science, LLM locaux et RAG",
        "Interaction Personnes-Systèmes (IHM)",
        "Je cherche mon stage de fin d'études en Data & IA",
    ]
    slot, size = 5.0, 19
    cw = size * 0.602
    total = slot * len(roles)
    # effet machine à écrire : la largeur du masque avance par pas
    typing = []
    caret_vals, caret_kt = [], []
    for i, r in enumerate(roles):
        n = len(r)
        tw = n * cw
        x0 = cx - tw / 2
        vals, kts = [], []
        steps = 24
        def T(s):
            return (i * slot + s) / total
        vals.append(0); kts.append(0.0)
        if i:
            vals.append(0); kts.append(T(0))
        for s in range(1, steps + 1):
            vals.append(tw * s / steps); kts.append(T(1.6 * s / steps))
        vals.append(tw); kts.append(T(4.2))
        for s in range(1, 7):
            vals.append(tw * (1 - s / 6)); kts.append(T(4.2 + 0.5 * s / 6))
        if kts[-1] < 1:
            vals.append(0); kts.append(1.0)
        V = ";".join(f"{v:.0f}" for v in vals)
        K = ";".join(f"{k:.4f}" for k in kts)
        typing.append(
            f'<clipPath id="c{i}"><rect x="{x0:.0f}" y="350" width="0" height="34">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" calcMode="discrete" values="{V}" keyTimes="{K}"/>'
            f'</rect></clipPath>')
        caret_vals.append((x0, vals, kts))
    clip_defs = "".join(typing)
    texts = "".join(
        f'<text clip-path="url(#c{i})" x="{cx}" y="374" text-anchor="middle" font-family="{MONO}" font-size="{size}" fill="#B9C3FF">{e(r)}</text>'
        for i, r in enumerate(roles))
    # curseur : suit la fin du texte de chaque phrase
    cv, ck = [], []
    for i, (x0, vals, kts) in enumerate(caret_vals):
        lo, hi = i * slot / total, (i + 1) * slot / total
        for v, k in zip(vals, kts):
            if lo <= k < hi and (not ck or k > ck[-1]):
                cv.append(x0 + v); ck.append(k)
    cv.append(cv[0]); ck.append(1.0)
    ck[0] = 0.0
    caret = (f'<rect x="{cv[0]:.0f}" y="356" width="2" height="23" fill="{INDIGO}" class="blink">'
             f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" calcMode="discrete" '
             f'values="{";".join(f"{v+3:.0f}" for v in cv)}" keyTimes="{";".join(f"{k:.4f}" for k in ck)}"/></rect>')

    defs = (bg_defs(0.5, 0.25)
            + clip_defs
            + f'<radialGradient id="core"><stop offset="0" stop-color="#FFF6E8" stop-opacity=".95"/><stop offset=".25" stop-color="{VIOLET}" stop-opacity=".55"/><stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/></radialGradient>'
            + f'<radialGradient id="neb1"><stop offset="0" stop-color="{INDIGO}" stop-opacity=".22"/><stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/></radialGradient>'
            + f'<radialGradient id="neb2"><stop offset="0" stop-color="#C85BFF" stop-opacity=".14"/><stop offset="1" stop-color="#C85BFF" stop-opacity="0"/></radialGradient>'
            + f'<linearGradient id="ring" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{HALO}"/><stop offset=".5" stop-color="{VIOLET}" stop-opacity=".2"/><stop offset="1" stop-color="{INDIGO}"/></linearGradient>'
            + f'<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{STAR}"/><stop offset=".45" stop-color="{STAR}"/><stop offset=".5" stop-color="#C9D2FF"/><stop offset=".55" stop-color="{STAR}"/><stop offset="1" stop-color="{STAR}"/>'
            + '<animate attributeName="x1" values="-1;1" dur="7s" repeatCount="indefinite"/><animate attributeName="x2" values="0;2" dur="7s" repeatCount="indefinite"/></linearGradient>'
            + f'<radialGradient id="horizon" cx=".5" cy="0" r=".6"><stop offset="0" stop-color="{HALO}" stop-opacity=".55"/><stop offset="1" stop-color="{HALO}" stop-opacity="0"/></radialGradient>'
            + '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>'
            + '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>'
            + f'<clipPath id="av"><circle cx="{cx}" cy="{cy}" r="62"/></clipPath>'
            + f'<clipPath id="card"><rect width="{W}" height="{H}" rx="22"/></clipPath>')

    style = (".gx path{vector-effect:non-scaling-stroke}.blink{animation:bl 1s steps(1) infinite}@keyframes bl{50%{opacity:0}}"
             ".breathe{animation:br 6s ease-in-out infinite}@keyframes br{0%,100%{opacity:.55}50%{opacity:1}}"
             ".pulse{animation:pu 2s ease-out infinite;transform-box:fill-box;transform-origin:center}"
             "@keyframes pu{0%{transform:scale(1);opacity:.7}100%{transform:scale(3);opacity:0}}"
             ".rise{animation:ri 1.4s cubic-bezier(.2,.7,.2,1) both}@keyframes ri{from{opacity:0;transform:translateY(14px)}}"
             ".fade{animation:fa 2.4s ease-out both}@keyframes fa{from{opacity:0}}")

    avoid = lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < 70 ** 2
    body = [frame(W, H), '<g clip-path="url(#card)">',
            '<ellipse cx="300" cy="140" rx="380" ry="200" fill="url(#neb1)" class="breathe"/>',
            '<ellipse cx="940" cy="260" rx="360" ry="220" fill="url(#neb2)" class="breathe" style="animation-delay:-3s"/>',
            f'<g class="drift2">{starfield(W, H, 150, 1, (.3, 1.1), avoid)}</g>',
            f'<g class="drift">{starfield(W, H, 70, 2, (.6, 1.7), avoid)}</g>',
            shooting([(1050, 70, 1), (820, 40, 4.5), (1150, 220, 7.2)]),
            # galaxie spirale inclinée, en rotation lente
            f'<g class="fade" transform="translate({cx} {cy}) rotate(-14) scale(1 .4)">'
            '<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="140s" repeatCount="indefinite"/>'
            f'{spiral()}</g></g>',
            f'<ellipse cx="{cx}" cy="{cy}" rx="190" ry="80" fill="url(#core)" class="breathe" transform="rotate(-14 {cx} {cy})"/>',
            # orbite + lune
            f'<ellipse id="orb" cx="{cx}" cy="{cy}" rx="112" ry="34" fill="none" stroke="{HALO}" stroke-opacity=".25" stroke-dasharray="2 5" transform="rotate(-14 {cx} {cy})"/>',
            # photo
            f'<circle cx="{cx}" cy="{cy}" r="76" fill="{VIOLET}" opacity=".35" filter="url(#blur)" class="breathe"/>',
            f'<circle cx="{cx}" cy="{cy}" r="66" fill="{VOID}"/>',
            f'<image href="data:image/jpeg;base64,{avatar_b64}" xlink:href="data:image/jpeg;base64,{avatar_b64}" x="{cx-62}" y="{cy-62}" width="124" height="124" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>',
            f'<circle cx="{cx}" cy="{cy}" r="67" fill="none" stroke="url(#ring)" stroke-width="2.5">'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="12s" repeatCount="indefinite"/></circle>',
            # lune qui passe devant (moitié avant de l'orbite)
            f'<g transform="rotate(-14 {cx} {cy})"><circle r="5" fill="{HALO}"><animateMotion dur="9s" repeatCount="indefinite" '
            f'path="M{cx+112},{cy} A112,34 0 1,1 {cx-112},{cy} A112,34 0 1,1 {cx+112},{cy}"/></circle>'
            f'<circle r="11" fill="{HALO}" opacity=".25" filter="url(#soft)"><animateMotion dur="9s" repeatCount="indefinite" '
            f'path="M{cx+112},{cy} A112,34 0 1,1 {cx-112},{cy} A112,34 0 1,1 {cx+112},{cy}"/></circle></g>',
            # nom + frappe
            f'<text class="rise" x="{cx}" y="330" text-anchor="middle" font-family="{SANS}" font-size="58" font-weight="700" letter-spacing="-1" fill="url(#name)">Adam Hassen</text>',
            f'<g class="fade" style="animation-delay:.6s">{texts}{caret}</g>',
            f'<g class="rise" style="animation-delay:.9s">{pills_centered(cx, 404, ["Data Science", "IHM", "Full-stack", "Marchés financiers", "LLM locaux"])}</g>',
            # horizon planétaire
            f'<ellipse cx="{cx}" cy="1210" rx="1080" ry="700" fill="url(#horizon)" filter="url(#blur)" class="breathe"/>',
            f'<ellipse cx="{cx}" cy="1230" rx="1060" ry="700" fill="{VOID}"/>',
            f'<ellipse cx="{cx}" cy="1230" rx="1060" ry="700" fill="none" stroke="{HALO}" stroke-opacity=".7" stroke-width="1.5" class="breathe"/>',
            f'<text x="{cx}" y="575" text-anchor="middle" font-family="{SANS}" font-size="13" letter-spacing="6" fill="{MUTED}">LE MANS · TUNIS · EN ORBITE</text>',
            # barre du haut façon « agent local »
            f'<text x="34" y="44" font-family="{MONO}" font-size="13" fill="{MUTED}">github.com/adam-hassen</text>',
            f'<rect x="926" y="24" width="244" height="32" rx="16" fill="#FFFFFF" fill-opacity=".03" stroke="#2A3160"/>',
            f'<circle cx="948" cy="40" r="4" fill="{GREEN}"/><circle cx="948" cy="40" r="4" fill="{GREEN}" class="pulse"/>',
            f'<text x="962" y="45" font-family="{MONO}" font-size="13" fill="#D7DCF5">ouvert à un stage PFE</text>',
            '</g>']
    return svg(W, H, "".join(body), style, defs)


# ─────────────────────── À PROPOS (chat agent) ───────────────────────
def about():
    W, H = 1200, 470
    cyc = 22
    q = "Présente-toi en quelques lignes."
    lines = [
        ("Élève ingénieur en 5e année, en double diplôme :", STAR),
        ("Data Science à ESPRIT (Tunis) et Interaction Personnes-Systèmes", STAR),
        ("à l'ENSIM, Le Mans Université.", STAR),
        ("En ce moment : IA appliquée à l'assurance, LLM locaux, RAG, machine learning.", "#C9D2FF"),
        ("Je cherche mon stage de fin d'études en Data & IA, mobile partout en France.", "#C9D2FF"),
        ("Un modèle ne vaut que ce que valent ses données.", VIOLET),
    ]

    def kf(name, t_in, t_out=19.5):
        a, b = t_in / cyc * 100, (t_in + .6) / cyc * 100
        c, d = t_out / cyc * 100, (t_out + .8) / cyc * 100
        return (f"@keyframes {name}{{0%,{a:.1f}%{{opacity:0;transform:translateY(8px)}}"
                f"{b:.1f}%,{c:.1f}%{{opacity:1;transform:none}}{d:.1f}%,100%{{opacity:0}}}}"
                f".{name}{{animation:{name} {cyc}s ease-out infinite}}")

    style = kf("m0", .4)
    # points « en train d'écrire »
    style += (f"@keyframes dots{{0%,{1.6/cyc*100:.1f}%{{opacity:0}}{2/cyc*100:.1f}%,{4/cyc*100:.1f}%{{opacity:1}}{4.3/cyc*100:.1f}%,100%{{opacity:0}}}}"
              f".dots{{animation:dots {cyc}s infinite}}"
              ".bob{animation:bob 1s ease-in-out infinite}@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}")
    for i in range(len(lines)):
        style += kf(f"l{i}", 4.3 + i * 1.1)
    style += kf("meta", 4.3 + len(lines) * 1.1 + .3)

    body = [frame(W, H), f'<g opacity=".8">{starfield(W, H, 70, 11, (.3, 1))}</g>',
            # barre de fenêtre
            f'<circle cx="34" cy="34" r="6" fill="#FF5F57" opacity=".8"/><circle cx="54" cy="34" r="6" fill="#FEBC2E" opacity=".8"/><circle cx="74" cy="34" r="6" fill="#28C840" opacity=".8"/>',
            f'<text x="600" y="39" text-anchor="middle" font-family="{SANS}" font-size="14" fill="{MUTED}">Adam Agent · rien ne quitte la machine</text>',
            f'<rect x="1004" y="20" width="166" height="28" rx="14" fill="#FFFFFF" fill-opacity=".03" stroke="#2A3160"/>'
            f'<circle cx="1022" cy="34" r="4" fill="{GREEN}"/><text x="1034" y="39" font-family="{MONO}" font-size="12" fill="#D7DCF5">qwen3:8b · local</text>',
            f'<line x1="0" y1="62" x2="{W}" y2="62" stroke="{LINE}"/>']
    # bulle utilisateur
    qw = len(q) * 8.6 + 40
    body.append(f'<g class="m0"><rect x="{W-40-qw:.0f}" y="86" width="{qw:.0f}" height="42" rx="21" fill="{INDIGO}" fill-opacity=".18" stroke="{INDIGO}" stroke-opacity=".5"/>'
                f'<text x="{W-40-qw/2:.0f}" y="113" text-anchor="middle" font-family="{SANS}" font-size="16" fill="{STAR}">{e(q)}</text></g>')
    # avatar agent
    body.append(f'<circle cx="62" cy="168" r="18" fill="none" stroke="{HALO}" stroke-opacity=".6"/>'
                f'<circle cx="62" cy="168" r="5" fill="{HALO}"><animate attributeName="r" values="4;7;4" dur="2.4s" repeatCount="indefinite"/></circle>')
    body.append('<g class="dots">' + "".join(
        f'<circle class="bob" style="animation-delay:{i*.15}s" cx="{100+i*16}" cy="170" r="4" fill="{MUTED}"/>' for i in range(3)) + '</g>')
    y = 174
    for i, (t, col) in enumerate(lines):
        if i == 3 or i == 5:
            y += 14
        weight = ' font-style="italic"' if i == 5 else ""
        body.append(f'<text class="l{i}" x="100" y="{y}" font-family="{SANS}" font-size="19" fill="{col}"{weight}>{e(t)}</text>')
        y += 34
    body.append(f'<text class="meta" x="100" y="{y+16}" font-family="{MONO}" font-size="12" fill="{MUTED}">généré en local · 0 € · 0 octet envoyé</text>')
    # zone de saisie
    body.append(f'<rect x="40" y="{H-66}" width="{W-80}" height="44" rx="22" fill="#FFFFFF" fill-opacity=".02" stroke="#2A3160"/>'
                f'<text x="66" y="{H-38}" font-family="{SANS}" font-size="15" fill="#5B6385">Demande quelque chose…</text>'
                f'<circle cx="{W-64}" cy="{H-44}" r="15" fill="{STAR}"/><path d="M{W-64} {H-37}v-14m-6 6l6-6 6 6" stroke="{VOID}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    return svg(W, H, "".join(body), style, bg_defs(0.2, 0.0))


# ─────────────────────── PROJETS (planètes) ───────────────────────
def planet(cx, cy, r, c1, c2, ring=False, moon=True, seed=0, speed=14):
    rnd = random.Random(seed)
    pid = f"p{seed}"
    bands = "".join(
        f'<ellipse cx="{cx}" cy="{cy + rnd.uniform(-r*.8, r*.8):.1f}" rx="{r*1.2:.1f}" ry="{rnd.uniform(2, r*.12):.1f}" fill="{c2}" opacity="{rnd.uniform(.15,.4):.2f}"/>'
        for _ in range(6))
    defs = (f'<radialGradient id="{pid}g" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="{c1}"/><stop offset=".7" stop-color="{c2}"/><stop offset="1" stop-color="{VOID}"/></radialGradient>'
            f'<clipPath id="{pid}c"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
            f'<radialGradient id="{pid}h"><stop offset=".6" stop-color="{c1}" stop-opacity=".35"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient>')
    back_ring = front_ring = ""
    if ring:
        rr = f'rx="{r*1.9:.0f}" ry="{r*.45:.0f}" fill="none" stroke="{c1}" stroke-width="5" stroke-opacity=".45"'
        back_ring = f'<ellipse cx="{cx}" cy="{cy}" {rr} transform="rotate(-18 {cx} {cy})"/>'
        front_ring = (f'<clipPath id="{pid}f"><rect x="{cx-r*2.2:.0f}" y="{cy}" width="{r*4.4:.0f}" height="{r*2:.0f}" transform="rotate(-18 {cx} {cy})"/></clipPath>'
                      f'<ellipse cx="{cx}" cy="{cy}" {rr} transform="rotate(-18 {cx} {cy})" clip-path="url(#{pid}f)"/>')
    m = ""
    if moon:
        m = (f'<circle r="4" fill="#E8ECFF"><animateMotion dur="{speed*.6:.1f}s" repeatCount="indefinite" '
             f'path="M{cx+r*1.7},{cy} a{r*1.7},{r*.5} 0 1,1 {-r*3.4},0 a{r*1.7},{r*.5} 0 1,1 {r*3.4},0"/></circle>')
    body = (f'<circle cx="{cx}" cy="{cy}" r="{r*1.6:.0f}" fill="url(#{pid}h)" class="glow"/>{back_ring}'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{pid}g)"/>'
            f'<g clip-path="url(#{pid}c)"><g>{bands}<animateTransform attributeName="transform" type="translate" values="-{r*.4:.0f} 0;{r*.4:.0f} 0;-{r*.4:.0f} 0" dur="{speed}s" repeatCount="indefinite"/></g>'
            f'<circle cx="{cx + r*.45:.1f}" cy="{cy + r*.35:.1f}" r="{r*1.05:.1f}" fill="{VOID}" opacity=".55"/></g>{front_ring}{m}')
    return defs, body


def wrap(text, n):
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    out.append(cur)
    return out


def project_card(fname, title, sub, desc, tags, c1, c2, seed, ring=False, W=590, H=340, wrapn=58, planet_r=38):
    pdefs, pbody = planet(W - 96, 78, planet_r, c1, c2, ring=ring, seed=seed)
    y = 192
    desc_lines = "".join(
        f'<text x="32" y="{y + i*24}" font-family="{SANS}" font-size="15.5" fill="#BAC1DC">{e(l)}</text>'
        for i, l in enumerate(wrap(desc, wrapn)))
    x = 32
    tg = []
    for t in tags:
        p, w = pill(x, H - 58, t, size=13, pad=12)
        tg.append(p)
        x += w + 8
    style = (".glow{animation:gl 5s ease-in-out infinite}@keyframes gl{0%,100%{opacity:.6}50%{opacity:1}}"
             ".scan{animation:sc 6s ease-in-out infinite}@keyframes sc{0%{transform:translateX(-200px)}60%,100%{transform:translateX(" + str(W + 200) + "px)}}")
    defs = bg_defs(0.85, 0.2) + pdefs + (
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c1}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{c1}"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></linearGradient>'
        f'<clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    body = [frame(W, H), '<g clip-path="url(#cc)">', f'<g opacity=".9">{starfield(W, H, 45, seed + 50, (.3, 1))}</g>',
            f'<rect class="scan" x="0" y="0" width="160" height="1.5" fill="url(#edge)"/>',
            pbody,
            f'<text x="32" y="122" font-family="{SANS}" font-size="14" fill="{c1}">{e(sub)}</text>',
            f'<text x="32" y="156" font-family="{SANS}" font-size="24" font-weight="700" fill="{STAR}">{e(title)}</text>',
            desc_lines, "".join(tg), '</g>']
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(svg(W, H, "".join(body), style, defs))


def agent_card():
    W, H = 1200, 300
    cx, cy = 960, 150
    nodes = [("Disque", 0), ("RAM", 72), ("Projets", 144), ("Ménage", 216), ("Batterie", 288)]
    orbit = []
    for name, ang in nodes:
        orbit.append(
            f'<g><animateTransform attributeName="transform" type="rotate" from="{ang} {cx} {cy}" to="{ang+360} {cx} {cy}" dur="40s" repeatCount="indefinite"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx+118}" y2="{cy}" stroke="{INDIGO}" stroke-opacity=".25" stroke-dasharray="3 4"/>'
            f'<circle cx="{cx+118}" cy="{cy}" r="5" fill="{HALO}" class="tw1" style="animation-delay:-{ang/90:.1f}s"/>'
            f'<g transform="translate({cx+118} {cy})"><text y="-12" text-anchor="middle" font-family="{SANS}" font-size="12.5" fill="#C9D2FF">'
            f'<animateTransform attributeName="transform" type="rotate" from="{-ang}" to="{-ang-360}" dur="40s" repeatCount="indefinite"/>{name}</text></g></g>')
    desc = ("Mon assistant personnel qui tourne entièrement sur mon Mac avec Ollama et FastAPI. "
            "Il analyse le disque, la mémoire et la batterie, repère les apps gourmandes, retrouve un projet "
            "et l'ouvre dans VS Code. Lancé depuis le Dock, sans abonnement, rien ne quitte la machine.")
    lines = "".join(f'<text x="32" y="{140 + i*25}" font-family="{SANS}" font-size="16" fill="#BAC1DC">{e(l)}</text>'
                    for i, l in enumerate(wrap(desc, 78)))
    x, tg = 32, []
    for t in ["Python", "Ollama", "qwen3:8b", "FastAPI", "macOS", "100 % local"]:
        p, w = pill(x, H - 58, t, size=13, pad=12)
        tg.append(p)
        x += w + 8
    style = ".core{animation:co 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes co{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}"
    defs = bg_defs(0.8, 0.5) + (f'<radialGradient id="cg"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{VIOLET}"/>'
                                f'<stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/></radialGradient><clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    body = [frame(W, H), '<g clip-path="url(#cc)">', starfield(W, H, 90, 77, (.3, 1.1)),
            f'<circle cx="{cx}" cy="{cy}" r="118" fill="none" stroke="#2A3160"/>',
            f'<circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#2A3160" stroke-dasharray="1 6"/>',
            "".join(orbit),
            f'<circle class="core" cx="{cx}" cy="{cy}" r="34" fill="url(#cg)"/>',
            f'<text x="32" y="62" font-family="{SANS}" font-size="14" fill="{HALO}">Projet perso · en cours</text>',
            f'<text x="32" y="98" font-family="{SANS}" font-size="27" font-weight="700" fill="{STAR}">Adam Agent, une IA privée qui vit sur mon Mac</text>',
            lines, "".join(tg), '</g>']
    with open(os.path.join(OUT, "galaxy-agent.svg"), "w", encoding="utf-8") as f:
        f.write(svg(W, H, "".join(body), style, defs))


# ─────────────────────── STACK (constellations) ───────────────────────
def stack():
    W, H = 1200, 440
    groups = [
        ("Data Science & IA", HALO, 60, [
            ("Python", 90, 110), ("PyTorch", 210, 80), ("TensorFlow", 300, 150), ("scikit-learn", 180, 190),
            ("Hugging Face", 90, 260), ("Pandas", 250, 280), ("Power BI", 330, 350), ("Streamlit", 140, 360)],
         [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (4, 5), (5, 3), (5, 6), (4, 7)]),
        ("Développement", VIOLET, 420, [
            ("Java", 480, 120), ("Spring", 600, 90), ("Node.js", 700, 140), ("Next.js", 650, 230),
            ("Angular", 520, 230), ("JavaScript", 560, 330), ("C++", 720, 330), ("Flutter", 450, 360)],
         [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (4, 5), (5, 6), (3, 6), (5, 7)]),
        ("Données & MLOps", "#7FE3FF", 820, [
            ("SQL", 870, 110), ("Docker", 1000, 90), ("Git", 1110, 150), ("CI/CD", 1040, 220),
            ("MLOps", 900, 230), ("Jupyter", 960, 330), ("PL/SQL", 860, 350), ("Scrum", 1100, 320)],
         [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (4, 5), (5, 6), (3, 7), (5, 7)]),
    ]
    style = (".ln{stroke-dasharray:400;stroke-dashoffset:400;animation:dl 2.4s ease-out forwards}"
             "@keyframes dl{to{stroke-dashoffset:0}}"
             ".lbl{animation:fa 1.2s ease-out both}@keyframes fa{from{opacity:0}}"
             ".halo{animation:ha 3.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
             "@keyframes ha{0%,100%{transform:scale(.6);opacity:.2}50%{transform:scale(1.3);opacity:.6}}")
    body = [frame(W, H), starfield(W, H, 160, 21, (.3, 1.1)), shooting([(1100, 60, 2), (700, 30, 6)])]
    for gi, (name, col, tx, stars, edges) in enumerate(groups):
        d0 = gi * 0.8
        for k, (a, b) in enumerate(edges):
            (_, x1, y1), (_, x2, y2) = stars[a], stars[b]
            body.append(f'<line class="ln" style="animation-delay:{d0 + k*.15:.2f}s" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-opacity=".5" stroke-width="1.1"/>')
        for k, (lbl, x, y) in enumerate(stars):
            dl = d0 + k * .12
            big = 4.2 if k == 0 else 3
            body.append(f'<circle class="halo" style="animation-delay:-{k*.5:.1f}s" cx="{x}" cy="{y}" r="{big*3:.0f}" fill="{col}" opacity=".3"/>'
                        f'<circle cx="{x}" cy="{y}" r="{big}" fill="#fff"/>'
                        f'<text class="lbl" style="animation-delay:{dl:.2f}s" x="{x}" y="{y-12}" text-anchor="middle" font-family="{SANS}" font-size="14" fill="#DCE1F7">{e(lbl)}</text>')
        body.append(f'<text x="{tx + 150}" y="{H-24}" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="600" fill="{col}">{e(name)}</text>')
    with open(os.path.join(OUT, "galaxy-stack.svg"), "w", encoding="utf-8") as f:
        f.write(svg(W, H, "".join(body), style, bg_defs(0.5, 0.5)))


# ─────────────────────── TITRES DE SECTION ───────────────────────
def divider(fname, title, seed):
    W, H = 1200, 76
    tw = len(title) * 15.5
    style = (".glint{animation:gn 5s ease-in-out infinite}@keyframes gn{0%{transform:translateX(0);opacity:0}10%{opacity:1}70%{opacity:1}100%{transform:translateX(" + f"{W - tw - 120:.0f}" + "px);opacity:0}}")
    defs = (f'<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{INDIGO}" stop-opacity=".7"/>'
            f'<stop offset="1" stop-color="{INDIGO}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="gl"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{HALO}"/><stop offset="1" stop-color="{HALO}" stop-opacity="0"/></radialGradient>')
    x0 = 52 + tw + 20
    body = (f'<g transform="translate(20 38)"><path d="M0-9L2.5-2.5 9 0 2.5 2.5 0 9-2.5 2.5-9 0-2.5-2.5Z" fill="{STAR}" class="tw1"/></g>'
            f'<text x="44" y="47" font-family="{SANS}" font-size="27" font-weight="700" fill="{STAR}">{e(title)}</text>'
            f'<line x1="{x0:.0f}" y1="38" x2="{W}" y2="38" stroke="url(#ln)"/>'
            f'<circle class="glint" cx="{x0:.0f}" cy="38" r="9" fill="url(#gl)"/>'
            f'<g opacity=".6">{starfield(W, H, 14, seed, (.3, 1), lambda x, y: x < x0)}</g>')
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(svg(W, H, body, style, defs))


# ─────────────────────── PIED DE PAGE ───────────────────────
def footer():
    W, H = 1200, 220
    defs = (bg_defs(0.5, 1) + f'<radialGradient id="hz" cx=".5" cy="0" r=".6"><stop offset="0" stop-color="{HALO}" stop-opacity=".6"/><stop offset="1" stop-color="{HALO}" stop-opacity="0"/></radialGradient>'
            '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>'
            f'<clipPath id="cc"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    style = ".breathe{animation:br 6s ease-in-out infinite}@keyframes br{0%,100%{opacity:.5}50%{opacity:1}}"
    body = [frame(W, H), '<g clip-path="url(#cc)">', starfield(W, H, 80, 31, (.3, 1.1)), shooting([(1000, 40, 1.5)]),
            f'<ellipse cx="600" cy="880" rx="1000" ry="720" fill="url(#hz)" filter="url(#blur)" class="breathe"/>',
            f'<ellipse cx="600" cy="895" rx="980" ry="720" fill="{VOID}"/>',
            f'<ellipse cx="600" cy="895" rx="980" ry="720" fill="none" stroke="{HALO}" stroke-opacity=".7" stroke-width="1.5" class="breathe"/>',
            f'<text x="600" y="92" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="700" fill="{STAR}">Merci pour la visite</text>',
            f'<text x="600" y="126" text-anchor="middle" font-family="{SANS}" font-size="16" fill="#BAC1DC">Une idée, un stage, un projet ? Écris-moi : adam.hassen941@gmail.com</text>',
            '</g>']
    with open(os.path.join(OUT, "galaxy-footer.svg"), "w", encoding="utf-8") as f:
        f.write(svg(W, H, "".join(body), style, defs))


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "avatar.jpg"), "rb") as f:
        av = base64.b64encode(f.read()).decode()
    with open(os.path.join(OUT, "galaxy-hero.svg"), "w", encoding="utf-8") as f:
        f.write(hero(av))
    with open(os.path.join(OUT, "galaxy-about.svg"), "w", encoding="utf-8") as f:
        f.write(about())
    agent_card()
    project_card("galaxy-assurance.svg", "Services intelligents pour l'assurance", "Recherche appliquée · 2026–2027",
                 "Agent de personnalisation des offres avec un petit LLM local, conseiller RAG qui analyse un contrat "
                 "en citant ses sources, et benchmark de la sévérité des sinistres : ML classique contre architectures hybrides.",
                 ["Python", "LLM", "RAG", "Fine-tuning"], "#7FE3FF", "#2457C5", 1, ring=True)
    project_card("galaxy-bourse.svg", "Prédiction des marchés boursiers", "Projet académique",
                 "Plateforme de prédiction sur séries temporelles. Extraction automatique depuis plusieurs APIs de marché, "
                 "harmonisation de sources hétérogènes, feature engineering et modèles de deep learning.",
                 ["Python", "LSTM", "Time Series", "APIs"], "#FFC27A", "#C2562A", 2)
    project_card("galaxy-crypto.svg", "Crypto Due Diligence", "Projet académique",
                 "Site web d'analyse de cryptomonnaies développé en Python avec Dash, avec une banque de "
                 "questions-réponses basée sur le modèle de langage Mistral-7B.",
                 ["Python", "Dash", "Mistral-7B", "NLP"], "#C9A6FF", "#5B2DB8", 3, ring=True)
    project_card("galaxy-vermeg.svg", "Monitoring prédictif des logs", "Stage · Vermeg · assurance",
                 "Tableau de bord de surveillance des logs en temps réel : classification automatique des erreurs "
                 "et modèle prédictif pour anticiper les incidents et identifier leurs causes probables.",
                 ["Python", "Machine Learning", "Dashboard"], "#7DF0B5", "#1E7A63", 4)
    stack()
    for fn, t, s in [("galaxy-h-about.svg", "À propos", 41), ("galaxy-h-projets.svg", "Projets", 42),
                     ("galaxy-h-stack.svg", "Ma constellation technique", 43), ("galaxy-h-stats.svg", "Statistiques", 44),
                     ("galaxy-h-contrib.svg", "Contributions", 45)]:
        divider(fn, t, s)
    footer()
    print("SVG générés dans", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
