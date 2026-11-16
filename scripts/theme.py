"""Produit une variante claire et une variante sombre d'un SVG.

Les SVG sont écrits avec des variables CSS (:root{--x:…}) et un bloc
@media (prefers-color-scheme:dark). Dans une balise <img>, ce media query suit
le système et non le thème choisi sur GitHub : on fige donc deux fichiers,
que le README choisit avec <picture>, et on remplace chaque var(--x) par sa
valeur (certains navigateurs ignorent var() dans les attributs SVG).
"""
import os
import re

DARK = "@media (prefers-color-scheme:dark){"


def _blocks(text):
    """Renvoie [(début, fin_contenu, fin_bloc)] des blocs @media sombres."""
    out, i = [], 0
    while True:
        s = text.find(DARK, i)
        if s < 0:
            return out
        depth, j = 1, s + len(DARK)
        while depth:
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
            j += 1
        out.append((s, s + len(DARK), j - 1, j))
        i = j


def _resolve(text):
    vars_ = {}
    for block in re.findall(r":root\{([^{}]*)\}", text):
        for k, v in re.findall(r"--([\w-]+)\s*:\s*([^;}]+)", block):
            vars_[k] = v.strip()
    text = re.sub(r":root\{[^{}]*\}", "", text)
    for _ in range(3):  # variables qui en référencent d'autres
        text = re.sub(r"var\(--([\w-]+)\)", lambda m: vars_.get(m.group(1), m.group(0)), text)
    return text


def variant(text, mode):
    parts, last = [], 0
    for s, cs, ce, end in _blocks(text):
        parts.append(text[last:s])
        if mode == "dark":
            parts.append(text[cs:ce])
        last = end
    parts.append(text[last:])
    return _resolve("".join(parts))


def write_pair(folder, name, text):
    """Écrit name-light.svg et name-dark.svg."""
    base = name[:-4] if name.endswith(".svg") else name
    for mode in ("light", "dark"):
        with open(os.path.join(folder, f"{base}-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(variant(text, mode))
