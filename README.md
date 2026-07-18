# SiteHealth

> **Website health scanner — one command, three modes.**
> _Open-source alternative to manual site checks._

![Demo](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9%2B-orange)

---

## Quick Start

```bash
pip install sitehealth
sitehealth example.com
```

## Three Modes

### 1. Scan — Check a single site

```bash
sitehealth example.com --fix
```

```
  SiteHealth v0.2.0
  URL: https://example.com
  ==========================================
  Health: 75/100 (B)
  ==========================================
  HTTPS:   ok (expires in 187d)
  Robots:  present
  Sitemap: missing
  Title:   yes
  Desc:    yes
  JSON-LD: no
  Speed:   342ms
  ==========================================
```

With `--fix` you get actionable recommendations:

```
  [HIGH] SSL cert expires in 12d — renew now
  [MED]  Add a sitemap.xml to help crawlers discover your pages
  [MED]  Add JSON-LD structured data:
         <script type="application/ld+json">
         {"@context": "https://schema.org",
          "@type": "Organization",
          "name": "Your Brand",
          "url": "https://example.com"}
         </script>
```

### 2. Compare — Side-by-side audit

```bash
sitehealth --compare openai.com anthropic.com google.com
```

```
  URL                              Score   HTTPS    Robot    Site     Title  Desc   LD     Speed
  ================================================================================
  https://openai.com               85/100  ok       present  missing  ok     ok     ok     1240ms
  https://anthropic.com            70/100  ok       present  missing  ok     ok     no     892ms
  https://google.com               85/100  ok       missing  present  ok     ok     ok     84ms
```

### 3. Watch — Continuous monitoring

```bash
sitehealth --url https://example.com --watch 3600
```

Re-scans every hour, alerts you when something changes.

---

## What It Checks

| Check | Why |
|-------|-----|
| **HTTPS** | SSL cert validity + expiry warning |
| **robots.txt** | Controls crawler access |
| **sitemap.xml** | Helps crawlers find content |
| **Title tag** | Core SEO + social snippet |
| **Meta description** | Search result preview |
| **JSON-LD** | Structured data for rich results |
| **Load speed** | User experience + ranking |

---

## Install

```bash
# From PyPI
pip install sitehealth

# From source
git clone https://github.com/biuta666/sitehealth.git
cd sitehealth
pip install -e .
```

Requirements: Python 3.9+, httpx (auto-installed)

---

## Comparison

| Feature | SiteHealth | BuiltWith | Wappalyzer |
|---------|------------|-----------|------------|
| Price | **Free** | $295/mo | $250/mo |
| Setup | **1 command** | Multi-step | Extension |
| Compare mode | **Yes** | No | No |
| Watch mode | **Yes** | No | No |
| Fix suggestions | **Yes** | No | No |
| Open source | **MIT** | No | No |

---

## License

MIT — use it, modify it, share it.
