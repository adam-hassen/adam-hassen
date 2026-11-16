"""Génère la bannière du profil (assets/header.svg).

Une seule animation : une série temporelle qui se dessine, puis sa prévision.
Fond transparent et couleurs adaptées au thème clair ou sombre de GitHub.
Usage : python scripts/build_header.py
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "header.svg")
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"

W, H = 1200, 300
# zone du graphique
GX0, GX1, GY0, GY1 = 700, 1170, 62, 236
SPLIT = 0.72  # part « historique » ; le reste est la prévision


def series(n=64, seed=11):
    rnd = random.Random(seed)
    v, out = 0.0, []
    for i in range(n):
        v += rnd.gauss(0.06, 0.55)
        out.append(v + 1.6 * math.sin(i / 7.0))
    return out


def to_pts(vals, lo, hi, start, count):
    pts = []
    for i, v in enumerate(vals):
        x = GX0 + (GX1 - GX0) * (start + i) / (count - 1)
        y = GY1 - (GY1 - GY0) * (v - lo) / (hi - lo)
        pts.append((x, y))
    return pts


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


def build():
    vals = series()
    n = len(vals)
    k = int(n * SPLIT)
    hist, fut = vals[:k], vals[k - 1:]
    # prévision : tendance lissée + bande d'incertitude qui s'élargit
    slope = (hist[-1] - hist[-12]) / 11
    fc = [hist[-1] + slope * i * 0.8 for i in range(len(fut))]
    band = [0.4 + 0.22 * i for i in range(len(fut))]
    lo = min(min(hist), min(f - b for f, b in zip(fc, band))) - 1
    hi = max(max(hist), max(f + b for f, b in zip(fc, band))) + 1

    ph = to_pts(hist, lo, hi, 0, n)
    pf = to_pts(fc, lo, hi, k - 1, n)
    up = to_pts([f + b for f, b in zip(fc, band)], lo, hi, k - 1, n)
    dn = to_pts([f - b for f, b in zip(fc, band)], lo, hi, k - 1, n)
    d_hist, d_fc = smooth(ph), smooth(pf)
    d_band = smooth(up) + " L" + smooth(list(reversed(dn)))[1:] + " Z"
    area = d_hist + f" L{ph[-1][0]:.1f},{GY1} L{ph[0][0]:.1f},{GY1} Z"
    sx, sy = ph[-1]
    ex, ey = pf[-1]

    grid = "".join(f'<line class="rule" x1="{GX0}" x2="{GX1}" y1="{GY0 + (GY1-GY0)*i/3:.0f}" y2="{GY0 + (GY1-GY0)*i/3:.0f}"/>' for i in range(4))

    css = f"""
:root{{--ink:#1A2238;--muted:#5E6782;--rule:#E3E7F0;--acc:#2F5BEA;--acc2:#0E9F8F;--dot:#0E9F8F}}
@media (prefers-color-scheme:dark){{:root{{--ink:#E8ECF6;--muted:#97A0B8;--rule:#262D40;--acc:#7C9CFF;--acc2:#3CCFBE;--dot:#3CCFBE}}}}
.name{{fill:var(--ink);font:700 54px {SANS};letter-spacing:-1.2px}}
.role{{fill:var(--acc);font:600 22px {SANS}}}
.line{{fill:var(--muted);font:400 17px {SANS}}}
.cap{{fill:var(--muted);font:400 12.5px {SANS}}}
.rule{{stroke:var(--rule);stroke-width:1}}
.hist{{fill:none;stroke:var(--ink);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.4s cubic-bezier(.45,0,.2,1) .2s forwards}}
.area{{fill:var(--acc);opacity:0;animation:show .9s ease-out 2.4s forwards}}
.fc{{fill:none;stroke:var(--acc2);stroke-width:2;stroke-dasharray:6 6;opacity:0;animation:show .8s ease-out 2.6s forwards}}
.band{{fill:var(--acc2);opacity:0;animation:band 1.2s ease-out 2.7s forwards}}
.now{{stroke:var(--muted);stroke-width:1;stroke-dasharray:2 4;opacity:0;animation:show .6s ease-out 2.4s forwards}}
.pt{{fill:var(--dot);opacity:0;animation:show .4s ease-out 3.2s forwards}}
.halo{{fill:none;stroke:var(--dot);stroke-width:1.5;opacity:0;transform-box:fill-box;transform-origin:center;
  animation:pulse 2.4s ease-out 3.4s infinite}}
.fadein{{opacity:0;animation:show .9s ease-out forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@keyframes show{{to{{opacity:1}}}}
@keyframes band{{to{{opacity:.14}}}}
@keyframes pulse{{0%{{transform:scale(1);opacity:.8}}100%{{transform:scale(3.2);opacity:0}}}}
.area-op{{opacity:.07}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}.band{{opacity:.14!important}}.halo{{opacity:0!important}}}}
"""
    body = f"""
<text class="name fadein" x="0" y="112">Adam Hassen</text>
<text class="role fadein" style="animation-delay:.25s" x="2" y="152">Data Scientist et ingénieur IHM en formation</text>
<text class="line fadein" style="animation-delay:.45s" x="2" y="196">Double diplôme d'ingénieur, ESPRIT (Tunis) et ENSIM (Le Mans)</text>
<text class="line fadein" style="animation-delay:.6s" x="2" y="224">Stage de fin d'études de 6 mois à partir de mars 2027</text>

{grid}
<g style="opacity:.07"><path class="area" d="{area}" style="animation-name:show"/></g>
<path class="band" d="{d_band}"/>
<line class="now" x1="{sx:.1f}" x2="{sx:.1f}" y1="{GY0-14}" y2="{GY1}"/>
<path class="hist" pathLength="1" d="{d_hist}"/>
<path class="fc" d="{d_fc}"/>
<circle class="pt" cx="{ex:.1f}" cy="{ey:.1f}" r="4"/>
<circle class="halo" cx="{ex:.1f}" cy="{ey:.1f}" r="4"/>
<text class="cap fadein" style="animation-delay:2.5s" x="{sx-8:.1f}" y="{GY0-20}" text-anchor="end">historique</text>
<text class="cap fadein" style="animation-delay:2.8s" x="{sx+8:.1f}" y="{GY0-20}">prévision</text>
"""
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Adam Hassen, Data Scientist et ingénieur IHM en formation">'
           f'<style>{css}</style>{body}</svg>')
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("Bannière écrite :", os.path.abspath(OUT))


if __name__ == "__main__":
    build()
