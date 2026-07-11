#!/bin/bash
# ─────────────────────────────────────────────────────────
# Download curated cybersecurity photos from Unsplash
# These are PERMANENT direct URLs that won't break
# ─────────────────────────────────────────────────────────

echo "Downloading curated cybersecurity images..."
echo "This may take a few minutes..."

# Create folders
mkdir -p static/images/photos/malware
mkdir -p static/images/photos/breaches
mkdir -p static/images/photos/vulnerabilities
mkdir -p static/images/photos/privacy
mkdir -p static/images/photos/threats
mkdir -p static/images/photos/research
mkdir -p static/images/photos/general
mkdir -p static/images/fallback

echo ""
echo "=== MALWARE ==="
curl -sL "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80" -o static/images/photos/malware/01.jpg && echo "  ✓ malware-01"
curl -sL "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80" -o static/images/photos/malware/02.jpg && echo "  ✓ malware-02"
curl -sL "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80" -o static/images/photos/malware/03.jpg && echo "  ✓ malware-03"
curl -sL "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80" -o static/images/photos/malware/04.jpg && echo "  ✓ malware-04"
curl -sL "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=800&q=80" -o static/images/photos/malware/05.jpg && echo "  ✓ malware-05"
curl -sL "https://images.unsplash.com/photo-1580894894513-541e068a3e2b?w=800&q=80" -o static/images/photos/malware/06.jpg && echo "  ✓ malware-06"
curl -sL "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80" -o static/images/photos/malware/07.jpg && echo "  ✓ malware-07"
curl -sL "https://images.unsplash.com/photo-1562813733-b31f71025d54?w=800&q=80" -o static/images/photos/malware/08.jpg && echo "  ✓ malware-08"
curl -sL "https://images.unsplash.com/photo-1560732488-6b0df240254a?w=800&q=80" -o static/images/photos/malware/09.jpg && echo "  ✓ malware-09"
curl -sL "https://images.unsplash.com/photo-1551808525-51a94da548ce?w=800&q=80" -o static/images/photos/malware/10.jpg && echo "  ✓ malware-10"

echo ""
echo "=== DATA BREACHES ==="
curl -sL "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80" -o static/images/photos/breaches/01.jpg && echo "  ✓ breach-01"
curl -sL "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80" -o static/images/photos/breaches/02.jpg && echo "  ✓ breach-02"
curl -sL "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80" -o static/images/photos/breaches/03.jpg && echo "  ✓ breach-03"
curl -sL "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80" -o static/images/photos/breaches/04.jpg && echo "  ✓ breach-04"
curl -sL "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80" -o static/images/photos/breaches/05.jpg && echo "  ✓ breach-05"
curl -sL "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80" -o static/images/photos/breaches/06.jpg && echo "  ✓ breach-06"
curl -sL "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&q=80" -o static/images/photos/breaches/07.jpg && echo "  ✓ breach-07"
curl -sL "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800&q=80" -o static/images/photos/breaches/08.jpg && echo "  ✓ breach-08"
curl -sL "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80" -o static/images/photos/breaches/09.jpg && echo "  ✓ breach-09"
curl -sL "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&q=80" -o static/images/photos/breaches/10.jpg && echo "  ✓ breach-10"

echo ""
echo "=== VULNERABILITIES ==="
curl -sL "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80" -o static/images/photos/vulnerabilities/01.jpg && echo "  ✓ vuln-01"
curl -sL "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80" -o static/images/photos/vulnerabilities/02.jpg && echo "  ✓ vuln-02"
curl -sL "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&q=80" -o static/images/photos/vulnerabilities/03.jpg && echo "  ✓ vuln-03"
curl -sL "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80" -o static/images/photos/vulnerabilities/04.jpg && echo "  ✓ vuln-04"
curl -sL "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80" -o static/images/photos/vulnerabilities/05.jpg && echo "  ✓ vuln-05"
curl -sL "https://images.unsplash.com/photo-1597733336794-12d05021d510?w=800&q=80" -o static/images/photos/vulnerabilities/06.jpg && echo "  ✓ vuln-06"
curl -sL "https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=800&q=80" -o static/images/photos/vulnerabilities/07.jpg && echo "  ✓ vuln-07"
curl -sL "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&q=80" -o static/images/photos/vulnerabilities/08.jpg && echo "  ✓ vuln-08"
curl -sL "https://images.unsplash.com/photo-1515879218367-8466d910adf9?w=800&q=80" -o static/images/photos/vulnerabilities/09.jpg && echo "  ✓ vuln-09"
curl -sL "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80" -o static/images/photos/vulnerabilities/10.jpg && echo "  ✓ vuln-10"

echo ""
echo "=== PRIVACY ==="
curl -sL "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&q=80" -o static/images/photos/privacy/01.jpg && echo "  ✓ privacy-01"
curl -sL "https://images.unsplash.com/photo-1484417894086-9e30f40f1059?w=800&q=80" -o static/images/photos/privacy/02.jpg && echo "  ✓ privacy-02"
curl -sL "https://images.unsplash.com/photo-1483389127117-b6a2102724ae?w=800&q=80" -o static/images/photos/privacy/03.jpg && echo "  ✓ privacy-03"
curl -sL "https://images.unsplash.com/photo-1423592707957-3b212afa6733?w=800&q=80" -o static/images/photos/privacy/04.jpg && echo "  ✓ privacy-04"
curl -sL "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80" -o static/images/photos/privacy/05.jpg && echo "  ✓ privacy-05"
curl -sL "https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?w=800&q=80" -o static/images/photos/privacy/06.jpg && echo "  ✓ privacy-06"
curl -sL "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?w=800&q=80" -o static/images/photos/privacy/07.jpg && echo "  ✓ privacy-07"
curl -sL "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80" -o static/images/photos/privacy/08.jpg && echo "  ✓ privacy-08"
curl -sL "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80" -o static/images/photos/privacy/09.jpg && echo "  ✓ privacy-09"
curl -sL "https://images.unsplash.com/photo-1563206767-5b18f218e8de?w=800&q=80" -o static/images/photos/privacy/10.jpg && echo "  ✓ privacy-10"

echo ""
echo "=== THREATS ==="
curl -sL "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80" -o static/images/photos/threats/01.jpg && echo "  ✓ threat-01"
curl -sL "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80" -o static/images/photos/threats/02.jpg && echo "  ✓ threat-02"
curl -sL "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80" -o static/images/photos/threats/03.jpg && echo "  ✓ threat-03"
curl -sL "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80" -o static/images/photos/threats/04.jpg && echo "  ✓ threat-04"
curl -sL "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80" -o static/images/photos/threats/05.jpg && echo "  ✓ threat-05"
curl -sL "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80" -o static/images/photos/threats/06.jpg && echo "  ✓ threat-06"
curl -sL "https://images.unsplash.com/photo-1597733336794-12d05021d510?w=800&q=80" -o static/images/photos/threats/07.jpg && echo "  ✓ threat-07"
curl -sL "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&q=80" -o static/images/photos/threats/08.jpg && echo "  ✓ threat-08"
curl -sL "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80" -o static/images/photos/threats/09.jpg && echo "  ✓ threat-09"
curl -sL "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=800&q=80" -o static/images/photos/threats/10.jpg && echo "  ✓ threat-10"

echo ""
echo "=== RESEARCH ==="
curl -sL "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80" -o static/images/photos/research/01.jpg && echo "  ✓ research-01"
curl -sL "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80" -o static/images/photos/research/02.jpg && echo "  ✓ research-02"
curl -sL "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&q=80" -o static/images/photos/research/03.jpg && echo "  ✓ research-03"
curl -sL "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80" -o static/images/photos/research/04.jpg && echo "  ✓ research-04"
curl -sL "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&q=80" -o static/images/photos/research/05.jpg && echo "  ✓ research-05"
curl -sL "https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80" -o static/images/photos/research/06.jpg && echo "  ✓ research-06"
curl -sL "https://images.unsplash.com/photo-1515879218367-8466d910adf9?w=800&q=80" -o static/images/photos/research/07.jpg && echo "  ✓ research-07"
curl -sL "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800&q=80" -o static/images/photos/research/08.jpg && echo "  ✓ research-08"
curl -sL "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80" -o static/images/photos/research/09.jpg && echo "  ✓ research-09"
curl -sL "https://images.unsplash.com/photo-1562813733-b31f71025d54?w=800&q=80" -o static/images/photos/research/10.jpg && echo "  ✓ research-10"

echo ""
echo "=== GENERAL ==="
curl -sL "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80" -o static/images/photos/general/01.jpg && echo "  ✓ general-01"
curl -sL "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80" -o static/images/photos/general/02.jpg && echo "  ✓ general-02"
curl -sL "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80" -o static/images/photos/general/03.jpg && echo "  ✓ general-03"
curl -sL "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80" -o static/images/photos/general/04.jpg && echo "  ✓ general-04"
curl -sL "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80" -o static/images/photos/general/05.jpg && echo "  ✓ general-05"
curl -sL "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80" -o static/images/photos/general/06.jpg && echo "  ✓ general-06"
curl -sL "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80" -o static/images/photos/general/07.jpg && echo "  ✓ general-07"
curl -sL "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80" -o static/images/photos/general/08.jpg && echo "  ✓ general-08"
curl -sL "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80" -o static/images/photos/general/09.jpg && echo "  ✓ general-09"
curl -sL "https://images.unsplash.com/photo-1597733336794-12d05021d510?w=800&q=80" -o static/images/photos/general/10.jpg && echo "  ✓ general-10"

echo ""
echo "=== FALLBACK ==="
curl -sL "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80" -o static/images/fallback/cyber-default.jpg && echo "  ✓ fallback"

echo ""
echo "=== DONE ==="
echo "Downloaded photos to static/images/photos/"
ls -la static/images/photos/*/  | head -20
du -sh static/images/photos/
