# data.py
# ─────────────────────────────────────────────────────────
# Temporary sample data for CyberNews.
# This file will be replaced by database queries on Day 6.
# For now it acts as our "fake database".
# ─────────────────────────────────────────────────────────

ARTICLES = [
    {
        'id':       1,
        'title':    'Critical Zero-Day Vulnerability Found in Windows Kernel',
        'summary':  'Security researchers have discovered a critical zero-day vulnerability affecting all modern versions of Windows, allowing attackers to gain SYSTEM privileges.',
        'body':     '''Security researchers at a leading cybersecurity firm have uncovered a critical zero-day vulnerability in the Windows kernel that affects all modern versions of the operating system. The flaw, which has been assigned a CVSS score of 9.8 (Critical), allows local attackers to escalate their privileges to SYSTEM level without any user interaction.

The vulnerability was discovered during routine penetration testing of enterprise environments. Researchers immediately reported the finding to Microsoft through responsible disclosure channels. Microsoft has confirmed the vulnerability and is working on an emergency patch.

Organizations are urged to implement workarounds immediately while waiting for the official patch. Security teams should monitor endpoints for unusual privilege escalation attempts and review access logs for signs of exploitation.

The vulnerability affects Windows 10, Windows 11, Windows Server 2019, and Windows Server 2022. Earlier versions of Windows that are no longer supported may also be affected but will not receive patches.''',
        'category': 'Vulnerabilities',
        'source':   'The Hacker News',
        'date':     'Dec 25, 2025',
        'image':    'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'featured': True,
        'tags':     ['Windows', 'Zero-Day', 'CVE', 'Microsoft'],
        'read_time': 4,
    },
    {
        'id':       2,
        'title':    'Major Data Breach Exposes 50 Million User Records',
        'summary':  'A leading social media platform suffered a massive data breach, exposing personal information including emails, phone numbers, and hashed passwords.',
        'body':     '''A major social media platform has confirmed a data breach affecting approximately 50 million user accounts. The exposed data includes email addresses, phone numbers, dates of birth, and hashed passwords.

The breach was discovered by an independent security researcher who found the data being sold on underground forums. The researcher notified the company, which launched an internal investigation confirming the incident.

Affected users are being notified via email and are strongly advised to change their passwords immediately. The company has also enabled mandatory two-factor authentication for all accounts showing signs of compromise.

Regulatory authorities in the European Union have been notified, and the company may face significant fines under GDPR regulations if found to have inadequate security measures in place.''',
        'category': 'Data Breaches',
        'source':   'SecurityWeek',
        'date':     'Dec 24, 2025',
        'image':    'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        'featured': False,
        'tags':     ['Data Breach', 'Social Media', 'GDPR', 'Privacy'],
        'read_time': 3,
    },
    {
        'id':       3,
        'title':    'New Ransomware Strain Targets Healthcare Sector',
        'summary':  'A sophisticated ransomware group has launched a coordinated attack against hospital networks across Europe, encrypting patient records and demanding millions.',
        'body':     '''A newly identified ransomware strain dubbed "MedLock" has been used in coordinated attacks against at least 12 hospital networks across Europe. The attacks have encrypted patient records, disrupted medical equipment, and forced several hospitals to revert to manual paper-based operations.

The ransomware operators are demanding payments ranging from $2 million to $8 million per institution. Security researchers believe the group behind the attacks has ties to a previously known Eastern European cybercriminal organization.

Healthcare organizations are being advised to immediately audit their network segmentation, ensure offline backups are current, and review remote access security. The FBI and Europol are coordinating an international response to the attacks.

Several hospitals have already paid ransoms to restore access to patient data, raising concerns about funding future criminal operations.''',
        'category': 'Malware',
        'source':   'Krebs on Security',
        'date':     'Dec 24, 2025',
        'image':    'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80',
        'featured': False,
        'tags':     ['Ransomware', 'Healthcare', 'Europe', 'MedLock'],
        'read_time': 5,
    },
    {
        'id':       4,
        'title':    'FBI Warns of Surge in AI-Powered Phishing Attacks',
        'summary':  'The FBI has issued an urgent warning about a dramatic increase in AI-generated phishing emails that are nearly indistinguishable from legitimate communications.',
        'body':     '''The Federal Bureau of Investigation has issued a public service announcement warning of a 400% increase in AI-generated phishing attacks over the past quarter. These attacks use large language models to craft highly convincing emails that mimic legitimate business communications with unprecedented accuracy.

Traditional phishing detection methods are proving inadequate against these new AI-generated messages, which contain no spelling errors, use contextually appropriate language, and can even reference recent public information about the target organization.

The FBI recommends organizations implement additional verification procedures for any email requesting sensitive information or financial transactions, regardless of how legitimate the message appears. Multi-factor authentication and security awareness training remain critical defenses.

Several major financial institutions have already reported significant losses attributed to these sophisticated phishing campaigns.''',
        'category': 'Threats',
        'source':   'FBI Cyber Division',
        'date':     'Dec 23, 2025',
        'image':    'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
        'featured': False,
        'tags':     ['Phishing', 'AI', 'FBI', 'Social Engineering'],
        'read_time': 4,
    },
    {
        'id':       5,
        'title':    'NSA Releases New Guidelines for Quantum-Safe Encryption',
        'summary':  'The National Security Agency published comprehensive guidelines for organizations to begin transitioning to post-quantum cryptographic algorithms before 2030.',
        'body':     '''The National Security Agency has published its highly anticipated guidelines for transitioning to post-quantum cryptographic algorithms. The document outlines a timeline for federal agencies and critical infrastructure operators to migrate away from algorithms that could be broken by future quantum computers.

The NSA recommends immediate adoption of CRYSTALS-Kyber for key encapsulation and CRYSTALS-Dilithium for digital signatures, both recently standardized by NIST. Organizations are advised to begin their cryptographic inventory now to identify systems requiring upgrades.

The guidance acknowledges that while large-scale quantum computers capable of breaking current encryption may still be years away, the threat of "harvest now, decrypt later" attacks — where adversaries collect encrypted data today to decrypt when quantum computers become available — makes immediate action necessary.

Critical infrastructure sectors including energy, finance, and telecommunications are given priority migration timelines.''',
        'category': 'Research',
        'source':   'NSA',
        'date':     'Dec 23, 2025',
        'image':    'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80',
        'featured': False,
        'tags':     ['Quantum', 'Encryption', 'NSA', 'Post-Quantum'],
        'read_time': 6,
    },
    {
        'id':       6,
        'title':    'Privacy Regulators Fine Tech Giant $2.3 Billion',
        'summary':  'European privacy regulators issued a record-breaking fine against a major tech company for systematic violations of GDPR data protection rules.',
        'body':     '''The European Data Protection Board has coordinated a record $2.3 billion fine against a major technology company found to have systematically violated GDPR data protection regulations over a three-year period.

The investigation found that the company collected and processed user data without adequate legal basis, failed to honor data deletion requests within required timeframes, and shared personal data with third-party advertisers without explicit consent.

This marks the largest GDPR fine ever issued and sends a clear message to technology companies that regulators are willing to impose significant financial penalties for privacy violations. The company has 90 days to pay the fine and implement court-ordered remediation measures.

Privacy advocates have praised the decision while noting that even this record fine represents only a fraction of the company's annual revenue.''',
        'category': 'Privacy',
        'source':   'Reuters',
        'date':     'Dec 22, 2025',
        'image':    'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
        'featured': False,
        'tags':     ['GDPR', 'Privacy', 'Fine', 'Europe', 'Regulation'],
        'read_time': 3,
    },
    {
        'id':       7,
        'title':    'Chinese APT Group Targets Government Infrastructure',
        'summary':  'A state-sponsored Chinese hacking group has been linked to a series of intrusions targeting government networks in Southeast Asia using novel malware.',
        'body':     '''Security researchers at Mandiant have published detailed findings linking a Chinese state-sponsored advanced persistent threat group, tracked as APT41, to a series of sophisticated intrusions targeting government networks across Southeast Asia.

The attacks used previously undocumented malware capable of evading modern endpoint detection and response solutions. The malware employs a novel technique of hiding malicious code within legitimate system processes, making detection extremely difficult.

Targeted countries include Vietnam, Thailand, Malaysia, and the Philippines, with the attacks focused on government ministries handling foreign affairs and defense. The intrusions are assessed to be primarily intelligence-gathering operations rather than destructive attacks.

Attribution to China was made based on code similarities to previously identified Chinese malware, infrastructure overlaps, and operational timing consistent with Chinese business hours.''',
        'category': 'Threats',
        'source':   'Mandiant',
        'date':     'Dec 22, 2025',
        'image':    'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
        'featured': False,
        'tags':     ['APT', 'China', 'Government', 'Espionage', 'Malware'],
        'read_time': 5,
    },
    {
        'id':       8,
        'title':    'Open Source Security Tool Gains Massive Adoption',
        'summary':  'A newly released open source penetration testing framework has been downloaded over 2 million times in its first month, becoming the go-to tool for security professionals.',
        'body':     '''An open source penetration testing framework released by a team of independent security researchers has achieved over 2 million downloads in its first month, unprecedented adoption for a security tool of its kind.

The framework, which automates many common penetration testing tasks while maintaining the flexibility professionals require, has been praised for its intuitive interface and comprehensive documentation. It supports testing web applications, network infrastructure, and cloud environments.

Major enterprises including Fortune 500 companies have reportedly adopted the tool for internal security assessments, validating its capabilities beyond the typical open source security tool user base.

The development team has announced plans to establish a foundation to govern the project's future development and ensure it remains free and open source, addressing concerns about potential commercialization.''',
        'category': 'Research',
        'source':   'GitHub Security',
        'date':     'Dec 21, 2025',
        'image':    'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80',
        'featured': False,
        'tags':     ['Open Source', 'Pentesting', 'Tools', 'Security'],
        'read_time': 3,
    },
    {
        'id':       9,
        'title':    'Supply Chain Attack Compromises 500 npm Packages',
        'summary':  'Attackers successfully injected malicious code into hundreds of popular npm packages, potentially affecting millions of JavaScript developers worldwide.',
        'body':     '''A sophisticated supply chain attack has compromised over 500 npm packages, injecting malicious code that steals environment variables, cryptographic keys, and authentication tokens from developer machines running the affected packages.

The attack was carried out by compromising the accounts of package maintainers through credential stuffing attacks using previously leaked passwords. The attackers then published malicious updates to popular packages, which were automatically downloaded by developers and CI/CD pipelines.

The malicious code executes during package installation and silently transmits sensitive data to attacker-controlled servers. Security researchers estimate the attack may have affected systems at thousands of organizations worldwide.

npm has revoked the malicious package versions and is implementing additional security measures including mandatory multi-factor authentication for all package publishers with high download counts.''',
        'category': 'Malware',
        'source':   'Snyk Security',
        'date':     'Dec 21, 2025',
        'image':    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
        'featured': False,
        'tags':     ['Supply Chain', 'npm', 'JavaScript', 'Malware'],
        'read_time': 4,
    },
]


def get_all_articles():
    """Return all articles."""
    return ARTICLES


def get_featured_article():
    """Return the first featured article, or the first article if none featured."""
    featured = [a for a in ARTICLES if a.get('featured')]
    return featured[0] if featured else ARTICLES[0]


def get_regular_articles():
    """Return all non-featured articles."""
    return [a for a in ARTICLES if not a.get('featured')]


def get_article_by_id(article_id):
    """Find and return a single article by its ID."""
    return next((a for a in ARTICLES if a['id'] == article_id), None)


def get_articles_by_category(category):
    """Return all articles matching a specific category."""
    return [a for a in ARTICLES if a['category'] == category]


def get_related_articles(article_id, count=3):
    """
    Return articles related to the given article.
    'Related' means: same category, but not the same article.
    """
    article  = get_article_by_id(article_id)
    if not article:
        return []

    related = [
        a for a in ARTICLES
        if a['category'] == article['category']
        and a['id']      != article_id
    ]
    return related[:count]


def search_articles(query):
    """
    Search articles by query string.
    Checks title, summary, category, source, and tags.
    """
    query = query.lower().strip()
    if not query:
        return ARTICLES

    results = []
    for article in ARTICLES:
        # Check multiple fields
        searchable = ' '.join([
            article['title'],
            article['summary'],
            article['category'],
            article['source'],
            ' '.join(article.get('tags', [])),
        ]).lower()

        if query in searchable:
            results.append(article)

    return results


def get_category_counts():
    """Return a dictionary of category → article count."""
    counts = {}
    for article in ARTICLES:
        cat = article['category']
        counts[cat] = counts.get(cat, 0) + 1
    return counts
