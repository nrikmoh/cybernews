from pathlib import Path
import random

BASE = Path("static/images/covers")

CATEGORIES = {
    "malware": {
        "label": "MALWARE",
        "sub": "Code • Infection • Ransomware",
        "colors": [("#7f1d1d", "#ef4444"), ("#3f0d12", "#a71d31"), ("#450a0a", "#dc2626")],
    },
    "breaches": {
        "label": "DATA BREACH",
        "sub": "Exposure • Leak • Compromise",
        "colors": [("#451a03", "#f59e0b"), ("#78350f", "#f97316"), ("#422006", "#d97706")],
    },
    "vulnerabilities": {
        "label": "VULNERABILITY",
        "sub": "CVE • Exploit • Patch",
        "colors": [("#2e1065", "#8b5cf6"), ("#312e81", "#6366f1"), ("#4c1d95", "#a855f7")],
    },
    "privacy": {
        "label": "PRIVACY",
        "sub": "Tracking • Data • Surveillance",
        "colors": [("#082f49", "#3b82f6"), ("#0c4a6e", "#06b6d4"), ("#172554", "#2563eb")],
    },
    "threats": {
        "label": "THREAT INTEL",
        "sub": "APT • Phishing • DDoS",
        "colors": [("#431407", "#f97316"), ("#4a044e", "#ec4899"), ("#3f1d0f", "#ea580c")],
    },
    "research": {
        "label": "RESEARCH",
        "sub": "Analysis • Report • Tooling",
        "colors": [("#052e16", "#10b981"), ("#064e3b", "#14b8a6"), ("#022c22", "#22c55e")],
    },
    "general": {
        "label": "CYBERNEWS",
        "sub": "Security • Intelligence • Daily",
        "colors": [("#0f172a", "#00d4ff"), ("#111827", "#7c3aed"), ("#020617", "#06b6d4")],
    },
}


def svg_for(category_slug, variant_index, label, subtitle, color_a, color_b):
    r = random.Random(f"{category_slug}-{variant_index}")

    circles = []
    for _ in range(7):
        cx = r.randint(40, 760)
        cy = r.randint(40, 410)
        radius = r.randint(10, 80)
        opacity = round(r.uniform(0.05, 0.18), 2)
        circles.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="rgba(255,255,255,{opacity})" />'
        )

    lines = []
    for _ in range(14):
        x1 = r.randint(0, 800)
        y1 = r.randint(0, 450)
        x2 = x1 + r.randint(-180, 180)
        y2 = y1 + r.randint(-120, 120)
        opacity = round(r.uniform(0.05, 0.18), 2)
        lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="rgba(255,255,255,{opacity})" stroke-width="1" />'
        )

    code_snippets = [
        "threat_detected()", "packet.inspect()", "alert.raise()",
        "auth.failed", "scan://active", "CVE-XXXX-XXXX",
        "zero-day", "forensics", "intel.feed", "IOC matched"
    ]
    code = r.choice(code_snippets)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_a}" />
      <stop offset="100%" stop-color="{color_b}" />
    </linearGradient>
  </defs>

  <rect width="800" height="450" fill="url(#g)" />
  <rect width="800" height="450" fill="rgba(0,0,0,0.18)" />

  <g opacity="0.08">
    <path d="M0 60 H800 M0 120 H800 M0 180 H800 M0 240 H800 M0 300 H800 M0 360 H800 M0 420 H800"
          stroke="white" stroke-width="1" />
    <path d="M80 0 V450 M160 0 V450 M240 0 V450 M320 0 V450 M400 0 V450 M480 0 V450 M560 0 V450 M640 0 V450 M720 0 V450"
          stroke="white" stroke-width="1" />
  </g>

  {''.join(circles)}
  {''.join(lines)}

  <g>
    <rect x="38" y="38" rx="14" ry="14" width="170" height="42" fill="rgba(255,255,255,0.12)" />
    <text x="55" y="65" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="700" fill="white">
      CYBERNEWS
    </text>
  </g>

  <g>
    <text x="52" y="270" font-family="Arial, Helvetica, sans-serif" font-size="44" font-weight="900" fill="white">
      {label}
    </text>
    <text x="52" y="305" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="500" fill="rgba(255,255,255,0.86)">
      {subtitle}
    </text>
  </g>

  <g opacity="0.9">
    <rect x="52" y="332" width="180" height="2" fill="rgba(255,255,255,0.7)" />
    <text x="52" y="362" font-family="Courier New, monospace" font-size="16" fill="rgba(255,255,255,0.9)">
      &gt; {code}
    </text>
  </g>

  <g opacity="0.12">
    <text x="560" y="390" font-family="Arial, Helvetica, sans-serif" font-size="96" font-weight="900" fill="white">
      {variant_index:02d}
    </text>
  </g>
</svg>
"""


def main():
    total = 0

    for slug, cfg in CATEGORIES.items():
        folder = BASE / slug
        folder.mkdir(parents=True, exist_ok=True)

        for i in range(1, 17):  # 16 covers per category
            palette = cfg["colors"][(i - 1) % len(cfg["colors"])]
            svg = svg_for(
                category_slug=slug,
                variant_index=i,
                label=cfg["label"],
                subtitle=cfg["sub"],
                color_a=palette[0],
                color_b=palette[1],
            )
            out = folder / f"{slug}-{i:02d}.svg"
            out.write_text(svg, encoding="utf-8")
            total += 1

    # default fallback image
    fallback = Path("static/images/fallback/cyber-default.svg")
    fallback.parent.mkdir(parents=True, exist_ok=True)
    fallback.write_text(
        svg_for(
            category_slug="fallback",
            variant_index=0,
            label="CYBERNEWS",
            subtitle="Fallback • Local • Reliable",
            color_a="#0f172a",
            color_b="#00d4ff",
        ),
        encoding="utf-8",
    )

    print(f"Generated {total} cover images + 1 fallback SVG")


if __name__ == "__main__":
    main()
