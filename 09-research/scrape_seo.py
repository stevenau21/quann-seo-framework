#!/usr/bin/env python3
"""Scrape 17 SEO pages from holisticseo.digital"""
import json
import re
import sys
import urllib.request
import urllib.error
import ssl

URLS = [
    "https://www.holisticseo.digital/python-seo/information-extraction/",
    "https://www.holisticseo.digital/on-page-seo/writing-tips-for-seo",
    "https://www.holisticseo.digital/marketing/seo-content-brief/",
    "https://www.holisticseo.digital/marketing/seo-content-strategy/",
    "https://www.holisticseo.digital/marketing/topical-map/",
    "https://www.holisticseo.digital/marketing/content-cluster/",
    "https://www.holisticseo.digital/marketing/pillar-page/",
    "https://www.holisticseo.digital/marketing/buyer-journey/",
    "https://www.holisticseo.digital/marketing/search-intent-in-seo/",
    "https://www.holisticseo.digital/marketing/entity-based-seo/",
    "https://www.holisticseo.digital/marketing/information-retrieval/",
    "https://www.holisticseo.digital/on-page-seo/evergreen-content/",
    "https://www.holisticseo.digital/on-page-seo/keyword/",
    "https://www.holisticseo.digital/marketing/semantic-content-network/",
    "https://www.holisticseo.digital/marketing/holistic-seo/",
    "https://www.holisticseo.digital/theoretical-seo/",
    "https://www.holisticseo.digital/theoretical-seo/information-retrieval/",
]

def clean_html(html):
    """Remove nav, scripts, CSS, ads from HTML and return cleaned text."""
    # Remove script and style blocks
    html = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<style[\s\S]*?</style>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<noscript[\s\S]*?</noscript>', '', html, flags=re.IGNORECASE)
    # Remove structural elements  
    html = re.sub(r'<nav[\s\S]*?</nav>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<header[\s\S]*?</header>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<footer[\s\S]*?</footer>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<aside[\s\S]*?</aside>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<svg[\s\S]*?</svg>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<iframe[\s\S]*?</iframe>', '', html, flags=re.IGNORECASE)
    # Remove comments
    html = re.sub(r'<!--[\s\S]*?-->', '', html)
    # Remove all HTML tags
    text = re.sub(r'<[^>]*>', ' ', html)
    # Decode entities
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&rsquo;', "'")
    text = text.replace('&lsquo;', "'")
    text = text.replace('&rdquo;', '"')
    text = text.replace('&ldquo;', '"')
    text = text.replace('&ndash;', '–')
    text = text.replace('&mdash;', '—')
    text = re.sub(r'&#?[a-z0-9]+;', ' ', text, flags=re.IGNORECASE)
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' \n', '\n', text)
    text = re.sub(r'\n ', '\n', text)
    # Remove boilerplate
    text = re.sub(r'Skip to content', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Menu|Search|Subscribe|Newsletter|Share|Tweet|Pin it|Facebook|Instagram|LinkedIn|Twitter)\b', '', text, flags=re.IGNORECASE)
    # Final trim
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if len(text) > 5000:
        text = text[:5000] + '...'
    return text

def extract_title(html):
    m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    if m:
        title = m.group(1)
        title = re.sub(r'\s*[-–|]\s*Holistic\s*SEO\s*$', '', title, flags=re.IGNORECASE)
        return title.strip()
    return ""

def fetch_page(url):
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml'
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='replace')
            return html, resp.status
    except urllib.error.HTTPError as e:
        return None, e.code
    except Exception as e:
        return None, str(e)

results = []
for url in URLS:
    print(f"Fetching: {url}", file=sys.stderr)
    html, status = fetch_page(url)
    
    if status == 404 or html is None:
        results.append({
            "url": url,
            "title": "",
            "content": f"SKIPPED: {status}",
            "skipped": True,
            "error": str(status)
        })
        print(f"  SKIPPED ({status})", file=sys.stderr)
        continue
    
    title = extract_title(html)
    cleaned = clean_html(html)
    results.append({
        "url": url,
        "title": title,
        "content": cleaned,
        "skipped": False,
        "error": None
    })
    print(f"  OK: {title[:60]}... ({len(cleaned)} chars)", file=sys.stderr)

print(json.dumps(results, indent=2))
