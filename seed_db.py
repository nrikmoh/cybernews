# seed_db.py
# ─────────────────────────────────────────────────────────
# Database seeder for CyberNews.
#
# Run this script ONCE to:
# 1. Create all database tables
# 2. Add sample categories
# 3. Add sample articles
#
# Usage:
#   python seed_db.py
#
# To reset the database completely:
#   python seed_db.py --reset
# ─────────────────────────────────────────────────────────

import sys
from app     import app, db
from models  import Article, Category, Newsletter
from datetime import datetime, timedelta


# ── Sample Categories ──────────────────────────────────
CATEGORIES = [
    {
        'name':        'Malware',
        'description': 'Ransomware, trojans, spyware, and malicious software analysis',
        'icon':        'fa-bug',
        'color':       'malware',
    },
    {
        'name':        'Data Breaches',
        'description': 'Incidents involving unauthorized access to sensitive data',
        'icon':        'fa-database',
        'color':       'data-breaches',
    },
    {
        'name':        'Vulnerabilities',
        'description': 'CVEs, zero-days, patches, and security advisories',
        'icon':        'fa-triangle-exclamation',
        'color':       'vulnerabilities',
    },
    {
        'name':        'Privacy',
        'description': 'GDPR, data protection, surveillance, and user rights',
        'icon':        'fa-user-shield',
        'color':       'privacy',
    },
    {
        'name':        'Research',
        'description': 'Academic papers, new techniques, and security tools',
        'icon':        'fa-flask',
        'color':       'research',
    },
    {
        'name':        'Threats',
        'description': 'APT groups, nation-state actors, and threat intelligence',
        'icon':        'fa-crosshairs',
        'color':       'threats',
    },
]


# ── Sample Articles ────────────────────────────────────
ARTICLES = [
    {
        'title':    'Critical Zero-Day Vulnerability Found in Windows Kernel',
        'summary':  'Security researchers have discovered a critical zero-day vulnerability affecting all modern versions of Windows, allowing attackers to gain SYSTEM privileges.',
        'body':     '''Security researchers at a leading cybersecurity firm have uncovered a critical zero-day vulnerability in the Windows kernel that affects all modern versions of the operating system. The flaw, which has been assigned a CVSS score of 9.8 (Critical), allows local attackers to escalate their privileges to SYSTEM level without any user interaction.

The vulnerability was discovered during routine penetration testing of enterprise environments. Researchers immediately reported the finding to Microsoft through responsible disclosure channels. Microsoft has confirmed the vulnerability and is working on an emergency patch.

Organizations are urged to implement workarounds immediately while waiting for the official patch. Security teams should monitor endpoints for unusual privilege escalation attempts and review access logs for signs of exploitation.

The vulnerability affects Windows 10, Windows 11, Windows Server 2019, and Windows Server 2022. Earlier versions of Windows that are no longer supported may also be affected but will not receive patches.

Security professionals recommend isolating affected systems from sensitive network segments until the patch is available and tested. Additional monitoring for unusual SYSTEM-level process creation is strongly advised.''',
        'category': 'Vulnerabilities',
        'source':   'The Hacker News',
        'image_url':'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80',
        'featured': True,
        'tags':     ['Windows', 'Zero-Day', 'CVE', 'Microsoft', 'Kernel'],
        'days_ago': 0,
    },
    {
        'title':    'Major Data Breach Exposes 50 Million User Records',
        'summary':  'A leading social media platform suffered a massive data breach, exposing personal information including emails, phone numbers, and hashed passwords.',
        'body':     '''A major social media platform has confirmed a data breach affecting approximately 50 million user accounts. The exposed data includes email addresses, phone numbers, dates of birth, and hashed passwords.

The breach was discovered by an independent security researcher who found the data being sold on underground forums. The researcher notified the company, which launched an internal investigation confirming the incident.

Affected users are being notified via email and are strongly advised to change their passwords immediately. The company has also enabled mandatory two-factor authentication for all accounts showing signs of compromise.

Regulatory authorities in the European Union have been notified, and the company may face significant fines under GDPR regulations if found to have inadequate security measures in place.

This incident highlights the critical importance of implementing proper data encryption, access controls, and regular security audits for organizations handling large volumes of personal data.''',
        'category': 'Data Breaches',
        'source':   'SecurityWeek',
        'image_url':'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80',
        'featured': False,
        'tags':     ['Data Breach', 'Social Media', 'GDPR', 'Privacy'],
        'days_ago': 1,
    },
    {
        'title':    'New Ransomware Strain Targets Healthcare Sector',
        'summary':  'A sophisticated ransomware group has launched a coordinated attack against hospital networks across Europe, encrypting patient records and demanding millions.',
        'body':     '''A newly identified ransomware strain dubbed MedLock has been used in coordinated attacks against at least 12 hospital networks across Europe. The attacks have encrypted patient records, disrupted medical equipment, and forced several hospitals to revert to manual paper-based operations.

The ransomware operators are demanding payments ranging from 2 million to 8 million dollars per institution. Security researchers believe the group behind the attacks has ties to a previously known Eastern European cybercriminal organization.

Healthcare organizations are being advised to immediately audit their network segmentation, ensure offline backups are current, and review remote access security. The FBI and Europol are coordinating an international response to the attacks.

Several hospitals have already paid ransoms to restore access to patient data, raising concerns about funding future criminal operations. Law enforcement agencies strongly advise against paying ransoms as it encourages further attacks.

The MedLock ransomware uses advanced evasion techniques to avoid detection by standard antivirus software and encrypts files using military-grade AES-256 encryption.''',
        'category': 'Malware',
        'source':   'Krebs on Security',
        'image_url':'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80',
        'featured': False,
        'tags':     ['Ransomware', 'Healthcare', 'Europe', 'MedLock'],
        'days_ago': 1,
    },
    {
        'title':    'FBI Warns of Surge in AI-Powered Phishing Attacks',
        'summary':  'The FBI has issued an urgent warning about a dramatic increase in AI-generated phishing emails that are nearly indistinguishable from legitimate communications.',
        'body':     '''The Federal Bureau of Investigation has issued a public service announcement warning of a 400 percent increase in AI-generated phishing attacks over the past quarter. These attacks use large language models to craft highly convincing emails that mimic legitimate business communications with unprecedented accuracy.

Traditional phishing detection methods are proving inadequate against these new AI-generated messages, which contain no spelling errors, use contextually appropriate language, and can even reference recent public information about the target organization.

The FBI recommends organizations implement additional verification procedures for any email requesting sensitive information or financial transactions, regardless of how legitimate the message appears. Multi-factor authentication and security awareness training remain critical defenses.

Several major financial institutions have already reported significant losses attributed to these sophisticated phishing campaigns. The total estimated losses across all reported incidents exceed 500 million dollars this quarter alone.

Security experts recommend implementing DMARC, DKIM, and SPF email authentication protocols, alongside user training programs that specifically address AI-generated content.''',
        'category': 'Threats',
        'source':   'FBI Cyber Division',
        'image_url':'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80',
        'featured': False,
        'tags':     ['Phishing', 'AI', 'FBI', 'Social Engineering'],
        'days_ago': 2,
    },
    {
        'title':    'NSA Releases New Guidelines for Quantum-Safe Encryption',
        'summary':  'The National Security Agency published comprehensive guidelines for organizations to begin transitioning to post-quantum cryptographic algorithms before 2030.',
        'body':     '''The National Security Agency has published its highly anticipated guidelines for transitioning to post-quantum cryptographic algorithms. The document outlines a timeline for federal agencies and critical infrastructure operators to migrate away from algorithms that could be broken by future quantum computers.

The NSA recommends immediate adoption of CRYSTALS-Kyber for key encapsulation and CRYSTALS-Dilithium for digital signatures, both recently standardized by NIST. Organizations are advised to begin their cryptographic inventory now to identify systems requiring upgrades.

The guidance acknowledges that while large-scale quantum computers capable of breaking current encryption may still be years away, the threat of harvest now decrypt later attacks, where adversaries collect encrypted data today to decrypt when quantum computers become available, makes immediate action necessary.

Critical infrastructure sectors including energy, finance, and telecommunications are given priority migration timelines. Federal agencies must complete their transitions by 2030 under the new mandate.

The NSA has also published technical implementation guides for each recommended algorithm, along with testing frameworks organizations can use to validate their implementations.''',
        'category': 'Research',
        'source':   'NSA',
        'image_url':'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=800&q=80',
        'featured': False,
        'tags':     ['Quantum', 'Encryption', 'NSA', 'Post-Quantum', 'NIST'],
        'days_ago': 2,
    },
    {
        'title':    'Privacy Regulators Fine Tech Giant $2.3 Billion',
        'summary':  'European privacy regulators issued a record-breaking fine against a major tech company for systematic violations of GDPR data protection rules.',
        'body':     '''The European Data Protection Board has coordinated a record 2.3 billion dollar fine against a major technology company found to have systematically violated GDPR data protection regulations over a three-year period.

The investigation found that the company collected and processed user data without adequate legal basis, failed to honor data deletion requests within required timeframes, and shared personal data with third-party advertisers without explicit consent.

This marks the largest GDPR fine ever issued and sends a clear message to technology companies that regulators are willing to impose significant financial penalties for privacy violations. The company has 90 days to pay the fine and implement court-ordered remediation measures.

Privacy advocates have praised the decision while noting that even this record fine represents only a fraction of the company annual revenue. Critics argue that fines alone are insufficient to drive meaningful behavioral change at large technology corporations.

The ruling also requires the company to appoint an independent privacy monitor and submit quarterly compliance reports to regulators for the next five years.''',
        'category': 'Privacy',
        'source':   'Reuters',
        'image_url':'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
        'featured': False,
        'tags':     ['GDPR', 'Privacy', 'Fine', 'Europe', 'Regulation'],
        'days_ago': 3,
    },
    {
        'title':    'Chinese APT Group Targets Government Infrastructure',
        'summary':  'A state-sponsored Chinese hacking group has been linked to a series of intrusions targeting government networks in Southeast Asia using novel malware.',
        'body':     '''Security researchers at Mandiant have published detailed findings linking a Chinese state-sponsored advanced persistent threat group, tracked as APT41, to a series of sophisticated intrusions targeting government networks across Southeast Asia.

The attacks used previously undocumented malware capable of evading modern endpoint detection and response solutions. The malware employs a novel technique of hiding malicious code within legitimate system processes, making detection extremely difficult without specialized tools.

Targeted countries include Vietnam, Thailand, Malaysia, and the Philippines, with the attacks focused on government ministries handling foreign affairs and defense. The intrusions are assessed to be primarily intelligence-gathering operations rather than destructive attacks.

Attribution to China was made based on code similarities to previously identified Chinese malware, infrastructure overlaps, and operational timing consistent with Chinese business hours. The Chinese government has denied all involvement.

Affected governments have been notified through appropriate channels and are implementing additional network monitoring and access controls based on the published indicators of compromise.''',
        'category': 'Threats',
        'source':   'Mandiant',
        'image_url':'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80',
        'featured': False,
        'tags':     ['APT', 'China', 'Government', 'Espionage', 'Malware'],
        'days_ago': 3,
    },
    {
        'title':    'Open Source Security Tool Gains Massive Adoption',
        'summary':  'A newly released open source penetration testing framework has been downloaded over 2 million times in its first month, becoming the go-to tool for security professionals.',
        'body':     '''An open source penetration testing framework released by a team of independent security researchers has achieved over 2 million downloads in its first month, unprecedented adoption for a security tool of its kind.

The framework, which automates many common penetration testing tasks while maintaining the flexibility professionals require, has been praised for its intuitive interface and comprehensive documentation. It supports testing web applications, network infrastructure, and cloud environments from a single unified interface.

Major enterprises including Fortune 500 companies have reportedly adopted the tool for internal security assessments, validating its capabilities beyond the typical open source security tool user base. Several managed security service providers have integrated it into their standard assessment workflows.

The development team has announced plans to establish a foundation to govern the project future development and ensure it remains free and open source. A commercial support tier is planned to fund ongoing development without compromising the core free offering.

Community contributions have already extended the tool with plugins for cloud security assessment, API testing, and automated compliance checking against major security frameworks.''',
        'category': 'Research',
        'source':   'GitHub Security',
        'image_url':'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800&q=80',
        'featured': False,
        'tags':     ['Open Source', 'Pentesting', 'Tools', 'Security'],
        'days_ago': 4,
    },
    {
        'title':    'Supply Chain Attack Compromises 500 npm Packages',
        'summary':  'Attackers successfully injected malicious code into hundreds of popular npm packages, potentially affecting millions of JavaScript developers worldwide.',
        'body':     '''A sophisticated supply chain attack has compromised over 500 npm packages, injecting malicious code that steals environment variables, cryptographic keys, and authentication tokens from developer machines running the affected packages.

The attack was carried out by compromising the accounts of package maintainers through credential stuffing attacks using previously leaked passwords. The attackers then published malicious updates to popular packages, which were automatically downloaded by developers and CI/CD pipelines worldwide.

The malicious code executes during package installation and silently transmits sensitive data to attacker-controlled servers hosted across multiple countries to complicate attribution and takedown efforts.

Security researchers estimate the attack may have affected systems at thousands of organizations worldwide. npm has revoked the malicious package versions and is implementing additional security measures including mandatory multi-factor authentication for all package publishers with high download counts.

Developers are advised to audit their package dependencies immediately, rotate any secrets that may have been exposed, and implement software composition analysis tools in their development pipelines to detect future supply chain compromises.''',
        'category': 'Malware',
        'source':   'Snyk Security',
        'image_url':'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
        'featured': False,
        'tags':     ['Supply Chain', 'npm', 'JavaScript', 'Malware'],
        'days_ago': 4,
    },
]


def seed():
    """Main seeding function."""

    with app.app_context():

        # ── Optional: Reset database ───────────────────
        if '--reset' in sys.argv:
            print('⚠️  Dropping all tables...')
            db.drop_all()
            print('✓  Tables dropped')

        # ── Create all tables ──────────────────────────
        print('Creating database tables...')
        db.create_all()
        print('✓  Tables created')

        # ── Check if already seeded ────────────────────
        if Article.query.first() and '--reset' not in sys.argv:
            print('ℹ️  Database already has data.')
            print('   Use --reset flag to wipe and reseed:')
            print('   python seed_db.py --reset')
            return

        # ── Seed Categories ────────────────────────────
        print('\nSeeding categories...')
        for cat_data in CATEGORIES:
            # Check if category already exists
            existing = Category.query.filter_by(
                name=cat_data['name']
            ).first()

            if not existing:
                cat = Category(
                    name        = cat_data['name'],
                    description = cat_data['description'],
                    icon        = cat_data['icon'],
                    color       = cat_data['color'],
                )
                db.session.add(cat)
                print(f'  + {cat_data["name"]}')

        db.session.commit()
        print('✓  Categories seeded')

        # ── Seed Articles ──────────────────────────────
        print('\nSeeding articles...')
        for i, article_data in enumerate(ARTICLES):

            # Calculate a realistic creation date
            days_ago   = article_data.get('days_ago', i)
            created_at = datetime.utcnow() - timedelta(days=days_ago)

            article = Article(
                title      = article_data['title'],
                summary    = article_data['summary'],
                body       = article_data['body'],
                category   = article_data['category'],
                source     = article_data['source'],
                image_url  = article_data['image_url'],
                featured   = article_data.get('featured', False),
                published  = True,
                created_at = created_at,
            )

            # Use the tags setter property
            article.tags = article_data.get('tags', [])

            db.session.add(article)
            print(f'  + [{article_data["category"]}] {article_data["title"][:60]}')

        db.session.commit()
        print('✓  Articles seeded')

        # ── Summary ────────────────────────────────────
        print(f'''
╔══════════════════════════════════════╗
║   ✅ Database seeded successfully!   ║
╠══════════════════════════════════════╣
║  Articles:   {Article.query.count():<27}║
║  Categories: {Category.query.count():<27}║
╚══════════════════════════════════════╝
        ''')


if __name__ == '__main__':
    seed()
