"""Shared colors, fonts and small SVG helpers for the profile graphics."""
from html import escape

THEMES = {
    "dark": {
        "bg": "#0B1018",
        "surface": "#111824",
        "chip": "#162030",
        "border": "#223044",
        "grid": "#1A2433",
        "text": "#E8EDF5",
        "muted": "#93A1B5",
        "faint": "#56657A",
        "violet": "#A78BFA",
        "cyan": "#22D3EE",
        "green": "#34D399",
        "amber": "#FBBF24",
        "glow": 0.30,
    },
    "light": {
        "bg": "#FCFCFE",
        "surface": "#FFFFFF",
        "chip": "#F2F4F9",
        "border": "#DCE2EC",
        "grid": "#EDF0F5",
        "text": "#0F172A",
        "muted": "#536175",
        "faint": "#9AA6B8",
        "violet": "#7C3AED",
        "cyan": "#0891B2",
        "green": "#059669",
        "amber": "#D97706",
        "glow": 0.14,
    },
}

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Code', Consolas, Menlo, monospace"

BASE_CSS = f"""
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.pulse{{animation:pulse 2.2s ease-in-out infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def text_width(s, size, mono=False, bold=False):
    """Rough rendered width, erring wide so layouts keep slack across system fonts."""
    if mono:
        return len(s) * size * 0.62
    per = 0.60 if bold else 0.54
    narrow = sum(1 for c in s if c in "ilIjt.,:;'|·! ")
    return (len(s) - narrow * 0.45) * size * per


def esc(s):
    return escape(s, quote=True)


def svg(width, height, title, desc, body, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
        f'<title id="title">{esc(title)}</title>\n<desc id="desc">{esc(desc)}</desc>\n'
        f"<style>{BASE_CSS}{css}</style>\n{body}\n</svg>\n"
    )
