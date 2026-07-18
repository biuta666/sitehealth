#!/usr/bin/env python3
"""SiteHealth v0.2.0. MIT License."""
import sys, json, argparse, re, socket, ssl, time
from urllib.parse import urlparse
from datetime import datetime
VERSION = "0.2.0"
def scan(url):
    p = urlparse(url)
    d = p.netloc or p.path
    b = f"{p.scheme}://{p.netloc}" if p.scheme else f"https://{d}"
    r = {"url": url, "checks": {}, "score": 0, "fixes": []}
    import httpx; c = httpx.Client(timeout=10, verify=False)
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((d, 443), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=d) as ss:
                cert = ss.getpeercert()
                r["checks"]["https"] = {"status": "ok"}
                if cert.get("notAfter"): r["fixes"].append({"s": "high", "c": "https", "m": f"SSL: {cert['notAfter']}"})
    except Exception as e:
        r["checks"]["https"] = {"status": "err"}
    for path, name in [("/robots.txt", "robots_txt"), ("/sitemap.xml", "sitemap")]:
        try:
            resp = c.get(b + path)
            ok = resp.status_code == 200
            r["checks"][name] = {"status": "ok" if ok else "miss"}
            if not ok: r["fixes"].append({"s": "med", "c": name, "m": f"Add {path}"})
        except: r["checks"][name] = {"status": "err"}
    try:
        resp = c.get(url)
        html = resp.text.lower()
        r["checks"]["page"] = {
            "title": bool(re.search(r"<title>(.+?)</title>", html, re.DOTALL)),
            "desc": bool(re.search(r"<meta[^>]*name=[\"']description[\"']", html)),
            "jsonld": bool(re.search(r"type=[\"']application/ld\+json[\"']", html)),
            "ms": round(resp.elapsed.total_seconds() * 1000, 0),
        }
        if not r["checks"]["page"]["desc"]: r["fixes"].append({"s": "low", "c": "desc", "m": "Add meta description"})
        if not r["checks"]["page"]["jsonld"]: r["fixes"].append({"s": "med", "c": "jsonld", "m": "Add JSON-LD schema"})
    except: r["checks"]["page"] = {"error": "load failed"}
    c.close()
    ch = r["checks"]
    r["score"] = sum([25 if ch.get("https",{}).get("status")=="ok" else 0, 20 if ch.get("robots_txt",{}).get("status")=="ok" else 0, 20 if ch.get("sitemap",{}).get("status")=="ok" else 0, 15 if ch.get("page",{}).get("title") else 0, 10 if ch.get("page",{}).get("desc") else 0, 10 if ch.get("page",{}).get("jsonld") else 0])
    return r
def show(d):
    g = "A" if d["score"]>=80 else "B" if d["score"]>=60 else "C" if d["score"]>=40 else "D"
    print(f"\n  SiteHealth v{VERSION}\n  URL: {d['url']}\n  {'='*42}\n  Health: {d['score']}/100 ({g})\n  {'='*42}")
    ch = d.get("checks",{})
    if "https" in ch: print(f"  HTTPS:   {ch['https'].get('status','?')}")
    if "robots_txt" in ch: print(f"  Robots:  {ch['robots_txt'].get('status','?')}")
    if "sitemap" in ch: print(f"  Sitemap: {ch['sitemap'].get('status','?')}")
    p = ch.get("page",{})
    if p: print(f"  Title:   {'yes' if p.get('title') else 'no'}\n  Desc:    {'yes' if p.get('desc') else 'no'}\n  JSON-LD: {'yes' if p.get('jsonld') else 'no'}\n  Speed:   {p.get('ms','?')}ms")
    print(f"  {'='*42}")
    for f in d.get("fixes",[]):
        t = "[H]" if f["s"]=="high" else "[M]" if f["s"]=="med" else "[L]"
        print(f"  {t} {f['m']}")
    print(f"  {'='*42}\n")
def main():
    p = argparse.ArgumentParser(description="SiteHealth")
    p.add_argument("target", nargs="?")
    p.add_argument("--url"); p.add_argument("--json", action="store_true")
    p.add_argument("--compare", nargs="*"); p.add_argument("--watch", type=int)
    args = p.parse_args()
    if args.compare:
        for u in args.compare: show(scan(u))
        return
    u = args.url or (f"https://{args.target}" if args.target else None)
    if not u: print("sitehealth example.com"); return
    d = scan(u)
    if args.json: print(json.dumps(d, indent=2))
    else: show(d)
if __name__ == "__main__":
    main()