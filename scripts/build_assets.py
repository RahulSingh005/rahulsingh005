"""Builds the static profile graphics in assets/ (header, about tiles, project cards).

Edit the data below and run:  python scripts/build_assets.py
"""
from pathlib import Path

from theme import THEMES, esc, svg, text_width

OUT = Path(__file__).resolve().parent.parent / "assets"

PILL = "Available for SDE roles"

TICKER = [
    ("now", "building BlinkChat: WebRTC calls and LLM summaries"),
    ("prev", "AI Trainer at Handshake AI, SDE intern at DNote"),
    ("stack", "React · Node.js · MongoDB · Python · Flask"),
]

TILES = [
    ("EDUCATION", "violet", "IIT Roorkee", "B.Tech, 2022 – 2026", "Graduated May 2026"),
    ("EXPERIENCE", "cyan", "Handshake AI", "AI Trainer, Jul – Oct 2026", "Before: SDE intern, DNote"),
    ("FOCUS", "amber", "Full-stack + AI", "MERN, Next.js, Python", "Real-time apps, LLM features"),
    ("STATUS", "green", "Open to work", "SDE, full-stack, backend", "Open to relocation"),
]

PROJECTS = [
    {
        "slug": "readwatch",
        "name": "ReadWatch",
        "tag": "AI · WEB PLATFORM",
        "accent": "violet",
        "status": "Live",
        "desc": ["Summarizes articles and YouTube videos with Gemini.",
                 "A Chrome extension queues pages as you browse."],
        "metrics": [("95%", "pages fetched"), ("17", "REST endpoints"), ("3", "services")],
        "stack": ["React", "Express", "MongoDB", "Flask", "Gemini"],
    },
    {
        "slug": "blinkchat",
        "name": "BlinkChat",
        "tag": "REAL-TIME · MESSAGING",
        "accent": "cyan",
        "status": "Live",
        "desc": ["MERN and Socket.io messenger with group chats,",
                 "WebRTC calls and LLM catch-up summaries."],
        "metrics": [("256", "members per group"), ("53", "REST endpoints"), ("52", "backend tests")],
        "stack": ["React", "Node.js", "MongoDB", "Socket.io", "WebRTC"],
    },
    {
        "slug": "stock-sentiment",
        "name": "Stock Sentiment Analysis",
        "tag": "ML · NLP",
        "accent": "amber",
        "status": "Notebook",
        "desc": ["Scores daily news sentiment with VADER and tests",
                 "whether it helps predict GOOGL and MSFT prices."],
        "metrics": [("46K", "headlines scored"), ("0.92", "R² on GOOGL"), ("250", "trading days")],
        "stack": ["Python", "scikit-learn", "Keras", "VADER"],
    },
    {
        "slug": "crop-prediction",
        "name": "Crop Prediction",
        "tag": "ML · WEB APP",
        "accent": "green",
        "status": "Live",
        "desc": ["Recommends a crop from soil nutrients, pH and",
                 "weather. Random Forest model served with Flask."],
        "metrics": [("99.3%", "test accuracy"), ("22", "crop classes"), ("7", "input features")],
        "stack": ["Python", "scikit-learn", "Flask", "Render"],
    },
]


def fits(s, size, room, **kw):
    w = text_width(s, size, **kw)
    assert w <= room, f"{s!r} needs ~{w:.0f}px, has {room}px"


def header(t):
    W, H = 1280, 360
    cx, cy = 1050, 180
    # The first ticker line is visible by default, so the header still reads right
    # anywhere animations don't run (static renders, reduced motion).
    css = """
@keyframes cycle{0%{opacity:0;transform:translateY(8px)}4%,30%{opacity:1;transform:none}
34%,100%{opacity:0;transform:translateY(-8px)}}
.tick{opacity:0;animation:cycle 12s ease-in-out infinite}
.t0{opacity:1;animation-delay:-1s}.t1{animation-delay:3s}.t2{animation-delay:7s}
@keyframes spin{to{transform:rotate(360deg)}}
.orbit{transform-origin:CXpx CYpx;animation:spin 48s linear infinite}
""".replace("CX", str(cx)).replace("CY", str(cy))
    ticks = []
    for i, (label, line) in enumerate(TICKER):
        fits(f"{label:<6}{line}", 20, 790, mono=True)
        ticks.append(
            f'<text class="mono tick t{i}" x="72" y="318" font-size="20">'
            f'<tspan fill="{t["violet"]}" font-weight="600">{label:<6}</tspan>'
            f'<tspan fill="{t["text"]}">{esc(line)}</tspan></text>'
        )
    tagline = ["Full-stack developer · B.Tech, IIT Roorkee '26",
               "Real-time web apps, Chrome extensions and LLM features."]
    for line in tagline:
        fits(line, 24, 760)
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
  <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.3" fill="{t['faint']}"/></pattern>
  <radialGradient id="fade" cx=".78" cy=".35" r=".75">
    <stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="dotmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <radialGradient id="glowV"><stop offset="0" stop-color="{t['violet']}" stop-opacity="{t['glow']}"/>
    <stop offset="1" stop-color="{t['violet']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="glowC"><stop offset="0" stop-color="{t['cyan']}" stop-opacity="{t['glow'] * 0.7:.3f}"/>
    <stop offset="1" stop-color="{t['cyan']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['text']}"/><stop offset=".55" stop-color="{t['violet']}"/>
    <stop offset="1" stop-color="{t['cyan']}"/></linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{t['violet']}"/><stop offset="1" stop-color="{t['cyan']}"/></linearGradient>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['bg']}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dotmask)"/>
  <circle cx="{cx}" cy="60" r="420" fill="url(#glowV)"/>
  <circle cx="140" cy="380" r="380" fill="url(#glowC)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="24" fill="none" stroke="{t['border']}"/>

<rect x="72" y="44" width="{text_width(PILL, 19, bold=True) + 56:.0f}" height="42" rx="21" fill="{t['surface']}" stroke="{t['border']}"/>
<circle class="pulse" cx="96" cy="65" r="6" fill="{t['green']}"/>
<text class="sans" x="114" y="71.5" font-size="19" font-weight="600" fill="{t['text']}">{PILL}</text>

<text class="sans" x="68" y="172" font-size="84" font-weight="700" letter-spacing="-2.5" fill="url(#name)">Rahul Singh</text>
<text class="sans" x="72" y="220" font-size="24" fill="{t['muted']}">{esc(tagline[0])}</text>
<text class="sans" x="72" y="252" font-size="24" fill="{t['muted']}">{esc(tagline[1])}</text>
<line x1="72" y1="280" x2="120" y2="280" stroke="url(#ring)" stroke-width="3" stroke-linecap="round"/>
{chr(10).join(ticks)}

<circle cx="{cx}" cy="{cy}" r="150" fill="url(#glowV)"/>
<circle cx="{cx}" cy="{cy}" r="132" fill="none" stroke="{t['border']}" stroke-dasharray="2 9" stroke-linecap="round"/>
<g class="orbit">
  <circle cx="{cx + 132}" cy="{cy}" r="6" fill="{t['violet']}"/>
  <circle cx="{cx - 66}" cy="{cy + 114.3:.1f}" r="4.5" fill="{t['cyan']}"/>
  <circle cx="{cx - 66}" cy="{cy - 114.3:.1f}" r="4.5" fill="{t['green']}"/>
</g>
<rect x="{cx - 88}" y="{cy - 88}" width="176" height="176" rx="44" fill="{t['surface']}" stroke="url(#ring)" stroke-width="2.5"/>
<text class="sans" x="{cx}" y="{cy + 29}" text-anchor="middle" font-size="82" font-weight="700" letter-spacing="-3" fill="url(#ring)">RS</text>
"""
    return svg(W, H, "Rahul Singh",
               "Full-stack developer, B.Tech IIT Roorkee 2026. Builds real-time web apps, Chrome "
               "extensions and LLM features. Available for SDE roles.", body, css)


def tiles(t):
    W, H, gap = 1280, 188, 20
    tw = (W - gap * 3) / 4
    parts = []
    for i, (eyebrow, accent, main, sub, sub2) in enumerate(TILES):
        x = i * (tw + gap)
        fits(main, 31, tw - 52, bold=True)
        fits(sub, 20, tw - 52)
        fits(sub2, 18, tw - 52)
        dot_cls = ' class="pulse"' if eyebrow == "STATUS" else ""
        parts.append(f"""
<g transform="translate({x:.1f} 1)">
  <rect x=".5" y=".5" width="{tw - 1:.1f}" height="{H - 3}" rx="18" fill="{t['surface']}" stroke="{t['border']}"/>
  <rect x="26" y="0" width="40" height="3" rx="1.5" fill="{t[accent]}"/>
  <circle{dot_cls} cx="31" cy="42" r="5" fill="{t[accent]}"/>
  <text class="mono" x="45" y="48" font-size="17" letter-spacing="1.2" fill="{t['muted']}">{eyebrow}</text>
  <text class="sans" x="26" y="98" font-size="31" font-weight="700" letter-spacing="-.5" fill="{t['text']}">{esc(main)}</text>
  <text class="sans" x="26" y="133" font-size="20" fill="{t['muted']}">{esc(sub)}</text>
  <text class="sans" x="26" y="162" font-size="18" fill="{t['faint']}">{esc(sub2)}</text>
</g>""")
    desc = "; ".join(f"{e.title()}: {m}, {s}, {s2}" for e, _, m, s, s2 in TILES)
    return svg(W, H, "About Rahul", desc, "".join(parts))


def card(t, p):
    W, H, pad = 560, 368, 30
    a = t[p["accent"]]
    fits(p["name"], 32, W - pad * 2, bold=True)
    for line in p["desc"]:
        fits(line, 19.5, W - pad * 2)
    status_live = p["status"] == "Live"
    status_w = text_width(p["status"], 16, bold=True)
    sx = W - pad - status_w
    tag_w = text_width(p["tag"], 15, mono=True) + 28
    col = (W - pad * 2) / 3
    metrics = []
    for i, (value, label) in enumerate(p["metrics"]):
        x = pad + i * col
        fits(label, 17, col - 8)
        metrics.append(
            f'<text class="sans" x="{x:.1f}" y="250" font-size="36" font-weight="700" letter-spacing="-1" fill="{a}">{esc(value)}</text>'
            f'<text class="sans" x="{x:.1f}" y="276" font-size="17" fill="{t["muted"]}">{esc(label)}</text>'
        )
    chips, x = [], pad
    for name in p["stack"]:
        w = text_width(name, 16) + 26
        chips.append(
            f'<rect x="{x:.1f}" y="305" width="{w:.1f}" height="32" rx="16" fill="{t["chip"]}" stroke="{t["border"]}"/>'
            f'<text class="sans" x="{x + w / 2:.1f}" y="326" font-size="16" text-anchor="middle" fill="{t["text"]}">{esc(name)}</text>'
        )
        x += w + 8
    assert x - 8 <= W - pad, f"{p['name']} chips overflow ({x - 8:.0f}px)"
    body = f"""
<defs>
  <clipPath id="clip"><rect width="{W}" height="{H}" rx="22"/></clipPath>
  <radialGradient id="glow"><stop offset="0" stop-color="{a}" stop-opacity="{t['glow'] * 0.8:.3f}"/>
    <stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#clip)">
  <rect width="{W}" height="{H}" fill="{t['surface']}"/>
  <circle cx="{W - 40}" cy="10" r="230" fill="url(#glow)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="none" stroke="{t['border']}"/>
<rect x="{pad}" y="26" width="{tag_w:.1f}" height="32" rx="9" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-opacity=".35"/>
<text class="mono" x="{pad + 14}" y="47.5" font-size="15" font-weight="600" letter-spacing="1" fill="{a}">{esc(p['tag'])}</text>
<circle{' class="pulse"' if status_live else ''} cx="{sx - 12:.1f}" cy="42" r="5" fill="{t['green'] if status_live else t['faint']}"/>
<text class="sans" x="{W - pad}" y="47.5" font-size="16" font-weight="600" text-anchor="end" fill="{t['muted']}">{p['status']}</text>
<text class="sans" x="{pad}" y="108" font-size="32" font-weight="700" letter-spacing="-.6" fill="{t['text']}">{esc(p['name'])}</text>
<text class="sans" x="{pad}" y="145" font-size="19.5" fill="{t['muted']}">{esc(p['desc'][0])}</text>
<text class="sans" x="{pad}" y="172" font-size="19.5" fill="{t['muted']}">{esc(p['desc'][1])}</text>
<line x1="{pad}" y1="198" x2="{W - pad}" y2="198" stroke="{t['border']}"/>
{''.join(metrics)}
{''.join(chips)}
"""
    desc = (f"{p['name']}. {' '.join(p['desc'])} "
            + ", ".join(f"{v} {l}" for v, l in p["metrics"]) + ". Built with " + ", ".join(p["stack"]) + ".")
    return svg(W, H, p["name"], desc, body)


def footer(t):
    W, H = 1280, 64
    body = f"""
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{t['violet']}" stop-opacity="0"/><stop offset=".3" stop-color="{t['violet']}"/>
  <stop offset=".7" stop-color="{t['cyan']}"/><stop offset="1" stop-color="{t['cyan']}" stop-opacity="0"/></linearGradient></defs>
<rect x="0" y="8" width="{W}" height="2" fill="url(#g)"/>
<text class="mono" x="{W / 2}" y="46" font-size="14" letter-spacing="2" text-anchor="middle" fill="{t['faint']}">RAHULSINGH005 · 2026</text>
"""
    return svg(W, H, "Footer", "Decorative divider", body)


def main():
    OUT.mkdir(exist_ok=True)
    for mode, t in THEMES.items():
        files = {f"header-{mode}.svg": header(t), f"about-{mode}.svg": tiles(t), f"footer-{mode}.svg": footer(t)}
        for p in PROJECTS:
            files[f"card-{p['slug']}-{mode}.svg"] = card(t, p)
        for name, content in files.items():
            (OUT / name).write_text(content, encoding="utf-8", newline="\n")
    print(f"wrote {len(list(OUT.glob('*.svg')))} files to {OUT}")


if __name__ == "__main__":
    main()
