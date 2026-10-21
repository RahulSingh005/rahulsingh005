"""Renders the contribution activity chart from the live GitHub contribution calendar.

Run by .github/workflows/activity.yml every hour. Locally:  python scripts/activity.py --out dist
Uses the GraphQL API when GITHUB_TOKEN is set, otherwise the public contributions page.
"""
import argparse
import json
import math
import os
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from theme import THEMES, esc, svg

QUERY = """query($login: String!) {
  user(login: $login) { contributionsCollection { contributionCalendar {
    weeks { contributionDays { date contributionCount } } } } }
}"""

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_graphql(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-activity"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {d["date"]: d["contributionCount"] for w in weeks for d in w["contributionDays"]}


def fetch_public_page(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "profile-activity"})
    with urllib.request.urlopen(req, timeout=30) as r:
        page = r.read().decode()
    ids = dict(re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="([^"]+)"', page))
    tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', page))
    days = {}
    for day, cell in ids.items():
        m = re.match(r"\s*(\d[\d,]*) contribution", tips.get(cell, ""))
        days[day] = int(m.group(1).replace(",", "")) if m else 0
    if not days:
        raise RuntimeError("no contribution cells found on the public page")
    return days


def load(user):
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            days = fetch_graphql(user, token)
            print(f"source: GraphQL API ({len(days)} days)")
            return days
        except Exception as e:  # fall back to the public page rather than skip an update
            print(f"GraphQL failed ({e}); using the public contributions page", file=sys.stderr)
    days = fetch_public_page(user)
    print(f"source: public contributions page ({len(days)} days)")
    return days


def stats(days):
    series = sorted((date.fromisoformat(d), c) for d, c in days.items())
    counts = [c for _, c in series]

    i = len(series) - 1
    if counts[i] == 0:  # today isn't over yet, so it doesn't break the streak
        i -= 1
    end, current = series[i][0] if i >= 0 else None, 0
    while i >= 0 and counts[i] > 0:
        current, i = current + 1, i - 1
    current_start = series[i + 1][0] if current else None

    longest, run, best_span = 0, 0, None
    for k, (d, c) in enumerate(series):
        run = run + 1 if c else 0
        if run > longest:
            longest, best_span = run, (series[k - run + 1][0], d)

    best_day = max(series, key=lambda s: s[1])

    weeks = defaultdict(int)
    for d, c in series:
        weeks[d - timedelta(days=(d.weekday() + 1) % 7)] += c
    weekday = [0] * 7
    for d, c in series:
        weekday[d.weekday()] += c

    return {
        "total": sum(counts),
        "current": current, "current_span": (current_start, end),
        "longest": longest, "longest_span": best_span,
        "best_day": best_day,
        "weeks": sorted(weeks.items()),
        "weekday": weekday,
    }


def short(d):
    return f"{d:%b} {d.day}"


def nice_step(top, ticks=4):
    raw = max(top, 1) / ticks
    mag = 10 ** math.floor(math.log10(raw))
    return next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)


def monotone_path(pts):
    """Fritsch-Carlson monotone cubic through the points: smooth, never overshoots below zero."""
    n = len(pts)
    if n < 2:
        return f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    d = [(pts[i + 1][1] - pts[i][1]) / (pts[i + 1][0] - pts[i][0]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            tau = 3 / math.hypot(a, b)
            m[i], m[i + 1] = tau * a * d[i], tau * b * d[i]
    out = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        h = (x1 - x0) / 3
        out.append(f"C{x0 + h:.1f},{y0 + m[i] * h:.1f} {x1 - h:.1f},{y1 - m[i + 1] * h:.1f} {x1:.1f},{y1:.1f}")
    return "".join(out)


def render(t, s, user, updated):
    W, H = 1280, 580
    parts = []

    # Tiles
    cs, ce = s["current_span"]
    ls = s["longest_span"]
    bd, bc = s["best_day"]
    tiles = [
        ("LAST 12 MONTHS", f"{s['total']:,}", "", "contributions", "violet"),
        ("CURRENT STREAK", str(s["current"]), " days" if s["current"] != 1 else " day",
         f"since {short(cs)}" if s["current"] else "starts with the next commit", "green"),
        ("LONGEST STREAK", str(s["longest"]), " days" if s["longest"] != 1 else " day",
         f"{short(ls[0])} – {short(ls[1])}" if ls else "no streak yet", "cyan"),
        ("BEST DAY", str(bc), " contributions" if bc != 1 else " contribution", f"on {short(bd)}, {bd.year}", "amber"),
    ]
    tw = (W - 80 - 3 * 16) / 4
    for i, (label, value, unit, sub, accent) in enumerate(tiles):
        x = 40 + i * (tw + 16)
        parts.append(f"""
<g transform="translate({x:.1f} 118)">
  <rect x=".5" y=".5" width="{tw - 1:.1f}" height="108" rx="16" fill="{t['bg']}" stroke="{t['border']}"/>
  <circle cx="26" cy="30" r="4" fill="{t[accent]}"/>
  <text class="mono" x="38" y="35" font-size="13" letter-spacing="1.4" fill="{t['muted']}">{label}</text>
  <text class="sans" x="22" y="78" font-size="38" font-weight="700" letter-spacing="-1" fill="{t['text']}">{value}<tspan font-size="17" font-weight="500" letter-spacing="0" fill="{t['muted']}">{unit}</tspan></text>
  <text class="sans" x="22" y="98" font-size="14" fill="{t['faint']}">{esc(sub)}</text>
</g>""")

    # Weekly area chart
    px0, px1, py0, py1 = 108, 868, 306, 500
    weeks = s["weeks"]
    top = max((c for _, c in weeks), default=0)
    step = nice_step(top)
    ymax = step * 4
    def X(i):
        return px0 + (px1 - px0) * i / max(len(weeks) - 1, 1)
    def Y(v):
        return py1 - (py1 - py0) * v / ymax
    grid = []
    for k in range(5):
        v = step * k
        y = Y(v)
        dash = "" if k == 0 else ' stroke-dasharray="3 5"'
        grid.append(f'<line x1="{px0}" y1="{y:.1f}" x2="{px1}" y2="{y:.1f}" stroke="{t["grid"]}"{dash}/>'
                    f'<text class="mono" x="{px0 - 14}" y="{y + 4:.1f}" font-size="12" text-anchor="end" fill="{t["faint"]}">{v:g}</text>')
    months, last_x = [], -99
    for i, (wk, _) in enumerate(weeks):
        first = wk + timedelta(days=6)
        if i == 0 or first.month != (wk - timedelta(days=1)).month or wk.day == 1:
            x = X(i)
            if x - last_x >= 44 and i < len(weeks) - 1:
                months.append(f'<text class="mono" x="{x:.1f}" y="526" font-size="12" text-anchor="middle" fill="{t["faint"]}">{first:%b}</text>')
                last_x = x
    pts = [(X(i), Y(c)) for i, (_, c) in enumerate(weeks)]
    line = monotone_path(pts)
    area = f"{line}L{pts[-1][0]:.1f},{py1}L{pts[0][0]:.1f},{py1}Z"
    peak_i = max(range(len(weeks)), key=lambda i: weeks[i][1])
    peak_x, peak_y = pts[peak_i]
    peak_label = f"{weeks[peak_i][1]} · week of {short(weeks[peak_i][0])}"
    label_w = len(peak_label) * 7.6 + 20
    lx = min(max(peak_x - label_w / 2, px0), px1 - label_w)
    ly = max(peak_y - 44, py0 - 26)
    last_x_pt, last_y_pt = pts[-1]
    parts.append(f"""
<defs>
  <linearGradient id="stroke" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['violet']}"/><stop offset="1" stop-color="{t['cyan']}"/></linearGradient>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{t['violet']}" stop-opacity="{0.38 if t is THEMES['dark'] else 0.22}"/>
    <stop offset="1" stop-color="{t['violet']}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="40.5" y="250.5" width="851" height="298" rx="16" fill="{t['bg']}" stroke="{t['border']}"/>
<text class="sans" x="64" y="282" font-size="15" font-weight="600" fill="{t['muted']}">Weekly contributions</text>
{''.join(grid)}
{''.join(months)}
<path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="url(#stroke)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<line x1="{peak_x:.1f}" y1="{peak_y:.1f}" x2="{peak_x:.1f}" y2="{ly + 26:.1f}" stroke="{t['faint']}" stroke-dasharray="2 3"/>
<rect x="{lx:.1f}" y="{ly:.1f}" width="{label_w:.1f}" height="26" rx="8" fill="{t['surface']}" stroke="{t['border']}"/>
<text class="mono" x="{lx + label_w / 2:.1f}" y="{ly + 17.5:.1f}" font-size="12" text-anchor="middle" fill="{t['text']}">{esc(peak_label)}</text>
<circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="5" fill="{t['surface']}" stroke="{t['violet']}" stroke-width="2.5"/>
<circle class="pulse" cx="{last_x_pt:.1f}" cy="{last_y_pt:.1f}" r="5" fill="{t['cyan']}"/>
""")

    # Weekday bars
    wd = s["weekday"]
    wmax = max(wd) or 1
    busiest = max(range(7), key=lambda i: wd[i])
    bars = []
    for i, v in enumerate(wd):
        y = 306 + i * 28
        w = max(192 * v / wmax, 3)
        hot = i == busiest and v > 0
        bars.append(
            f'<text class="mono" x="936" y="{y + 11}" font-size="13" fill="{t["text"] if hot else t["muted"]}">{WEEKDAYS[i]}</text>'
            f'<rect x="984" y="{y}" width="192" height="14" rx="7" fill="{t["grid"]}"/>'
            f'<rect x="984" y="{y}" width="{w:.1f}" height="14" rx="7" '
            f'fill="{t["cyan"] if hot else t["violet"]}" fill-opacity="{1 if hot else 0.55}"/>'
            f'<text class="mono" x="1216" y="{y + 11}" font-size="13" text-anchor="end" fill="{t["muted"]}">{v}</text>'
        )
    busiest_text = f"Most active on {DAY_NAMES[busiest]}s" if any(wd) else "No activity yet"
    parts.append(f"""
<rect x="912.5" y="250.5" width="327" height="298" rx="16" fill="{t['bg']}" stroke="{t['border']}"/>
<text class="sans" x="936" y="282" font-size="15" font-weight="600" fill="{t['muted']}">By weekday</text>
{''.join(bars)}
<text class="sans" x="936" y="526" font-size="14" fill="{t['faint']}">{busiest_text}</text>
""")

    head = f"""
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="{t['surface']}" stroke="{t['border']}"/>
<text class="sans" x="40" y="62" font-size="26" font-weight="700" letter-spacing="-.4" fill="{t['text']}">Contribution activity</text>
<text class="sans" x="40" y="90" font-size="15" fill="{t['muted']}">Last 12 months on github.com/{esc(user)}</text>
<rect x="{W - 40 - 312}" y="40" width="312" height="34" rx="17" fill="{t['bg']}" stroke="{t['border']}"/>
<circle class="pulse" cx="{W - 40 - 290}" cy="57" r="4.5" fill="{t['green']}"/>
<text class="mono" x="{W - 40 - 276}" y="61.5" font-size="13" fill="{t['muted']}">Updated {updated:%d %b %Y, %H:%M} UTC</text>
"""
    desc = (f"{s['total']} contributions in the last 12 months. Current streak {s['current']} days, "
            f"longest {s['longest']} days, best day {bc} contributions on {short(bd)}. "
            f"Most active on {DAY_NAMES[busiest]}s. Updated {updated:%d %b %Y %H:%M} UTC.")
    return svg(W, H, "Contribution activity", desc, head + "".join(parts))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="RahulSingh005")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    s = stats(load(args.user))
    updated = datetime.now(timezone.utc)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for mode, t in THEMES.items():
        (out / f"activity-{mode}.svg").write_text(render(t, s, args.user, updated), encoding="utf-8", newline="\n")
    print(f"total={s['total']} current={s['current']} longest={s['longest']} best={s['best_day'][1]} -> {out}")


if __name__ == "__main__":
    main()
