#!/usr/bin/env python3
"""SiteHealth v0.1.0 - AI Brand Presence Scanner. MIT License."""
import sys, json, argparse, re, socket, ssl
from urllib.parse import urlparse
from datetime import datetime

VERSION = "0.1.0"

def check_url(url):
    """Check a single URL for AI readiness. Returns dict."""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    base = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme else f"https://{domain}"
    result = {"url": url, "checks": {}, "score": 0}

    try:
        import httpx
        client = httpx.Client(timeout=10, verify=False)
    except ImportError:
        return {"url": url, "error": "pip install httpx", "score": 0}

    # 1. HTTPS check
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                result["checks"]["https"] = {"status": "ok", "cert": cert.get("notAfter", "unknown")}
    except Exception as e:
        result["checks"]["https"] = {"status": "error", "detail": str(e)[:50]}

    # 2. Robots.txt
    try:
        r = client.get(f"{base}/robots.txt")
        has_robots = r.status_code == 200
        blocked = "Disallow: /" in r.text if has_robots else False
        result["checks"]["robots_txt"] = {"status": "present" if has_robots else "missing",
                                          "blocks_all": blocked}
    except Exception as e:
        result["checks"]["robots_txt"] = {"status": "error"}

    # 3. Sitemap
    try:
        r = client.get(f"{base}/sitemap.xml")
        result["checks"]["sitemap"] = {"status": "present" if r.status_code == 200 else "missing"}
    except:
        result["checks"]["sitemap"] = {"status": "error"}

    # 4. Page load + meta
    try:
        r = client.get(url)
        html = r.text.lower()
        has_title = bool(re.search(r"<title>(.+?)</title>", html, re.DOTALL))
        has_desc = bool(re.search(r'<meta[^>]*name=["\']description["\']', html))
        has_jsonld = bool(re.search(r'type=["\']application/ld\+json["\']', html))
        load_ms = r.elapsed.total_seconds() * 1000
        result["checks"]["page"] = {"status": "ok", "load_ms": round(load_ms, 0),
                                    "title": has_title, "description": has_desc, "jsonld": has_jsonld}
    except Exception as e:
        result["checks"]["page"] = {"status": "error", "detail": str(e)[:50]}

    # Score: 0-100
    score = 0
    if result["checks"].get("https", {}).get("status") == "ok": score += 25
    if result["checks"].get("robots_txt", {}).get("status") == "present": score += 20
    if result["checks"].get("sitemap", {}).get("status") == "present": score += 20
    page = result["checks"].get("page", {})
    if page.get("title"): score += 15
    if page.get("description"): score += 10
    if page.get("jsonld"): score += 10
    result["score"] = score
    if "error" not in result: client.close()
    return result


def scan_brand(brand):
    """Scan a brand name across multiple checks."""
    domain = brand.lower().replace(" ", "").replace("'", "") + ".com"
    url = f"https://{domain}"
    result = check_url(url)
    return {"brand": brand, "domain": domain, "url_checked": url,
            "scan_time": datetime.now().isoformat()[:19], "version": VERSION,
            "score": result.get("score", 0), "checks": result.get("checks", {}),
            "error": result.get("error")}


def show(data):
    """Print report."""
    print(f"\n  SiteHealth v{VERSION}")
    print(f"  Brand: {data['brand']} -> {data['domain']}")
    print(f"  " + "=" * 45)
    grade = "A" if data["score"] >= 80 else ("B" if data["score"] >= 60 else
            "C" if data["score"] >= 40 else "D")
    print(f"  AI Readiness: {data['score']}/100 ({grade})")
    print(f"  " + "=" * 45)
    c = data.get("checks", {})
    if "https" in c: print(f"  HTTPS:      {c['https'].get('status', '?')}")
    if "robots_txt" in c: print(f"  robots.txt: {c['robots_txt'].get('status', '?')}")
    if "sitemap" in c: print(f"  sitemap:    {c['sitemap'].get('status', '?')}")
    p = c.get("page", {})
    if p: print(f"  Title:      {'yes' if p.get('title') else 'no'}")
    if p: print(f"  Desc:       {'yes' if p.get('description') else 'no'}")
    if p: print(f"  JSON-LD:    {'yes' if p.get('jsonld') else 'no'}")
    if p: print(f"  Load:       {p.get('load_ms', '?')}ms")
    if data.get("error"): print(f"  Error: {data['error']}")
    print(f"  " + "=" * 45)
    print()


def main():
    p = argparse.ArgumentParser(description="SiteHealth - Check if your site is ready for AI search")
    p.add_argument("brand", nargs="?", help="Brand name (e.g. OpenAI)")
    p.add_argument("--url", help="Direct URL to check")
    p.add_argument("--json", action="store_true", help="JSON output")
    args = p.parse_args()

    if args.url:
        data = check_url(args.url)
        data["scan_time"] = datetime.now().isoformat()[:19]
    elif args.brand:
        data = scan_brand(args.brand)
    else:
        # Demo mode: show example
        data = scan_brand("Example")
        print("(Demo mode - pass a brand name for real check)")

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        show(data)


if __name__ == "__main__":
    main()
