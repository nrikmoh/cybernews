from pathlib import Path
import random

BASE = Path("static/images/covers")

CATEGORIES = {
    "malware": {
        "label": "MALWARE",
        "sub": [
            "Ransomware • Trojan • Worm",
            "Code Injection • Payload • RAT",
            "Spyware • Backdoor • Rootkit",
            "Cryptominer • Keylogger • Dropper",
        ],
        "icons": ["&#9760;", "&#9888;", "&#9762;", "&#10006;"],
        "colors": [
            ("#7f1d1d", "#ef4444"), ("#3f0d12", "#a71d31"),
            ("#450a0a", "#dc2626"), ("#6b0f0f", "#f87171"),
            ("#3b0e0e", "#ff6b6b"), ("#2d0a0a", "#e74c3c"),
        ],
    },
    "breaches": {
        "label": "DATA BREACH",
        "sub": [
            "Records Exposed • Leak • Dump",
            "Credential Theft • Database Hack",
            "Unauthorized Access • Compromise",
            "PII Exposure • Data Exfiltration",
        ],
        "icons": ["&#128274;", "&#9889;", "&#128272;", "&#9888;"],
        "colors": [
            ("#451a03", "#f59e0b"), ("#78350f", "#f97316"),
            ("#422006", "#d97706"), ("#5c2d00", "#fbbf24"),
            ("#6b3a00", "#fb923c"), ("#4d2600", "#f59e0b"),
        ],
    },
    "vulnerabilities": {
        "label": "VULNERABILITY",
        "sub": [
            "CVE • Zero-Day • Exploit Chain",
            "Buffer Overflow • RCE • Injection",
            "Patch Tuesday • Security Advisory",
            "CVSS Critical • Attack Surface",
        ],
        "icons": ["&#128737;", "&#9888;", "&#128270;", "&#10060;"],
        "colors": [
            ("#2e1065", "#8b5cf6"), ("#312e81", "#6366f1"),
            ("#4c1d95", "#a855f7"), ("#3b0764", "#c084fc"),
            ("#1e1b4b", "#818cf8"), ("#4a1d96", "#7c3aed"),
        ],
    },
    "privacy": {
        "label": "PRIVACY",
        "sub": [
            "GDPR • Data Protection • Rights",
            "Surveillance • Tracking • Cookies",
            "Personal Data • Consent • Audit",
            "Encryption • Anonymity • VPN",
        ],
        "icons": ["&#128065;", "&#128274;", "&#128373;", "&#9670;"],
        "colors": [
            ("#082f49", "#3b82f6"), ("#0c4a6e", "#06b6d4"),
            ("#172554", "#2563eb"), ("#0e3654", "#0ea5e9"),
            ("#0b1d33", "#38bdf8"), ("#091c2e", "#60a5fa"),
        ],
    },
    "threats": {
        "label": "THREAT INTEL",
        "sub": [
            "APT Group • Campaign • Attribution",
            "Phishing • Social Engineering",
            "DDoS • Botnet • C2 Infrastructure",
            "Nation State • Espionage • IOC",
        ],
        "icons": ["&#127919;", "&#9876;", "&#128680;", "&#10070;"],
        "colors": [
            ("#431407", "#f97316"), ("#4a044e", "#ec4899"),
            ("#3f1d0f", "#ea580c"), ("#5c1a00", "#fb923c"),
            ("#4c0519", "#f43f5e"), ("#3d0c02", "#ff7043"),
        ],
    },
    "research": {
        "label": "RESEARCH",
        "sub": [
            "Analysis • Report • White Paper",
            "Tool Release • Framework • PoC",
            "Academic • Discovery • Technique",
            "Bug Bounty • Disclosure • Audit",
        ],
        "icons": ["&#128300;", "&#128200;", "&#9879;", "&#128295;"],
        "colors": [
            ("#052e16", "#10b981"), ("#064e3b", "#14b8a6"),
            ("#022c22", "#22c55e"), ("#0d3320", "#34d399"),
            ("#083d23", "#4ade80"), ("#0a3d2a", "#2dd4bf"),
        ],
    },
    "general": {
        "label": "CYBERNEWS",
        "sub": [
            "Security Intelligence Daily",
            "Threat Monitor • Alert Feed",
            "Breaking • Analysis • Advisory",
            "Cyber Defense • Response • Intel",
        ],
        "icons": ["&#128737;", "&#9889;", "&#127760;", "&#128272;"],
        "colors": [
            ("#0f172a", "#00d4ff"), ("#111827", "#7c3aed"),
            ("#020617", "#06b6d4"), ("#0b1120", "#818cf8"),
            ("#0a0f1a", "#22d3ee"), ("#0d1117", "#a78bfa"),
        ],
    },
}


def svg_cover(slug, index, label, subtitle, icon_char, color_a, color_b):
    """Generate a unique branded SVG cover image."""
    r = random.Random(f"{slug}-{index}")

    # Random decorative elements
    circles = ""
    for _ in range(r.randint(5, 12)):
        cx = r.randint(20, 780)
        cy = r.randint(20, 430)
        radius = r.randint(8, 100)
        opacity = round(r.uniform(0.03, 0.15), 3)
        circles += f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="rgba(255,255,255,{opacity})" />\n'

    # Random connecting lines
    lines = ""
    for _ in range(r.randint(8, 20)):
        x1 = r.randint(0, 800)
        y1 = r.randint(0, 450)
        x2 = x1 + r.randint(-200, 200)
        y2 = y1 + r.randint(-150, 150)
        opacity = round(r.uniform(0.04, 0.12), 3)
        lines += (
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="rgba(255,255,255,{opacity})" stroke-width="{r.choice([1,1,1,2])}" />\n'
        )

    # Random dots (like a network visualization)
    dots = ""
    for _ in range(r.randint(10, 30)):
        dx = r.randint(0, 800)
        dy = r.randint(0, 450)
        dr = r.uniform(1, 3)
        opacity = round(r.uniform(0.1, 0.4), 2)
        dots += f'<circle cx="{dx}" cy="{dy}" r="{dr}" fill="rgba(255,255,255,{opacity})" />\n'

    # Code snippets that appear faintly
    code_snippets = [
        "threat_detected()", "packet.inspect(src)",
        "alert.raise(level=CRIT)", "auth.verify(token)",
        "scan://192.168.x.x:443", "CVE-2025-XXXX",
        "forensics.analyze()", "IOC.match(hash)",
        "firewall.block(ip)", "ids.alert(sig_id)",
        "ssl.handshake()", "dns.resolve(target)",
        "exploit.execute()", "patch.apply(cve)",
        "log.monitor(auth)", "hash.verify(sha256)",
    ]
    code1 = r.choice(code_snippets)
    code2 = r.choice(code_snippets)

    # Variant number position varies
    num_x = r.choice([580, 600, 620, 640])
    num_y = r.choice([380, 390, 400, 410])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{color_a}" />
      <stop offset="100%" stop-color="{color_b}" />
    </linearGradient>
    <linearGradient id="shine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgba(255,255,255,0.08)" />
      <stop offset="100%" stop-color="rgba(255,255,255,0)" />
    </linearGradient>
  </defs>

  <!-- Background gradient -->
  <rect width="800" height="450" fill="url(#bg)" />
  <rect width="800" height="225" fill="url(#shine)" />
  <rect width="800" height="450" fill="rgba(0,0,0,0.15)" />

  <!-- Grid pattern -->
  <g opacity="0.06">
    <path d="M0 50H800 M0 100H800 M0 150H800 M0 200H800 M0 250H800 M0 300H800 M0 350H800 M0 400H800"
          stroke="white" stroke-width="1" />
    <path d="M100 0V450 M200 0V450 M300 0V450 M400 0V450 M500 0V450 M600 0V450 M700 0V450"
          stroke="white" stroke-width="1" />
  </g>

  <!-- Decorative elements -->
  {circles}
  {lines}
  {dots}

  <!-- Top left: CyberNews badge -->
  <g>
    <rect x="32" y="28" rx="10" ry="10" width="150" height="36" fill="rgba(255,255,255,0.12)" />
    <text x="46" y="52" font-family="Arial,Helvetica,sans-serif" font-size="17"
          font-weight="800" fill="white" letter-spacing="1">CYBERNEWS</text>
  </g>

  <!-- Top right: icon badge -->
  <g opacity="0.25">
    <text x="720" y="65" font-family="Arial,sans-serif" font-size="42"
          fill="white" text-anchor="middle">{icon_char}</text>
  </g>

  <!-- Main label -->
  <text x="46" y="260" font-family="Arial,Helvetica,sans-serif" font-size="48"
        font-weight="900" fill="white" letter-spacing="2">{label}</text>

  <!-- Subtitle -->
  <text x="46" y="295" font-family="Arial,Helvetica,sans-serif" font-size="18"
        font-weight="500" fill="rgba(255,255,255,0.8)">{subtitle}</text>

  <!-- Divider line -->
  <rect x="46" y="316" width="200" height="2" fill="rgba(255,255,255,0.5)" rx="1" />

  <!-- Code lines -->
  <text x="46" y="348" font-family="Courier New,monospace" font-size="14"
        fill="rgba(255,255,255,0.7)">&gt; {code1}</text>
  <text x="46" y="372" font-family="Courier New,monospace" font-size="14"
        fill="rgba(255,255,255,0.5)">&gt; {code2}</text>

  <!-- Variant number watermark -->
  <g opacity="0.08">
    <text x="{num_x}" y="{num_y}" font-family="Arial,sans-serif" font-size="120"
          font-weight="900" fill="white">{index:02d}</text>
  </g>

  <!-- Bottom accent line -->
  <rect x="0" y="444" width="800" height="6" fill="rgba(255,255,255,0.15)" />

</svg>"""


def main():
    total = 0

    for slug, cfg in CATEGORIES.items():
        folder = BASE / slug
        folder.mkdir(parents=True, exist_ok=True)

        num_variants = 24  # 24 covers per category

        for i in range(1, num_variants + 1):
            palette = cfg["colors"][(i - 1) % len(cfg["colors"])]
            subtitle = cfg["sub"][(i - 1) % len(cfg["sub"])]
            icon = cfg["icons"][(i - 1) % len(cfg["icons"])]

            svg = svg_cover(
                slug=slug,
                index=i,
                label=cfg["label"],
                subtitle=subtitle,
                icon_char=icon,
                color_a=palette[0],
                color_b=palette[1],
            )

            out = folder / f"{slug}-{i:02d}.svg"
            out.write_text(svg, encoding="utf-8")
            total += 1

    # Fallback default cover
    fb_folder = Path("static/images/fallback")
    fb_folder.mkdir(parents=True, exist_ok=True)

    fallback = svg_cover(
        slug="fallback",
        index=0,
        label="CYBERNEWS",
        subtitle="Security Intelligence Daily",
        icon_char="&#128737;",
        color_a="#0f172a",
        color_b="#00d4ff",
    )
    (fb_folder / "cyber-default.svg").write_text(fallback, encoding="utf-8")

    print(f"Generated {total} cover images + 1 fallback")
    print(f"Categories: {len(CATEGORIES)}")
    print(f"Variants per category: 24")


if __name__ == "__main__":
    main()
