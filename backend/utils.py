# backend/utils.py
# helper functions to extract simple URL features and safely trace redirects

import re, math, collections
from urllib.parse import urlparse
import requests
import tldextract

SUSPICIOUS_WORDS = ["login","secure","update","verify","account","bank","signin","password"]
SHORTENER_DOMAINS = ["bit.ly","tinyurl.com","t.co","goo.gl","is.gd"]

def simple_entropy(s: str) -> float:
    if not s: return 0.0
    counts = collections.Counter(s)
    probs = [c/len(s) for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs)

def looks_like_ip(hostname: str) -> bool:
    return bool(hostname) and re.fullmatch(r'\d{1,3}(\.\d{1,3}){3}', hostname) is not None

def extract_features(url: str) -> dict:
    url = (url or "").strip()
    parsed = urlparse(url)
    ext = tldextract.extract(url)
    host = parsed.hostname or ""
    registered_domain = ext.registered_domain or host
    features = {
        "url_length": len(url),
        "host_length": len(registered_domain),
        "host_entropy": simple_entropy(registered_domain),
        "has_ip": int(looks_like_ip(host)),
        "has_at_symbol": int("@" in url),
        "dot_count": host.count(".") if host else 0,
        "suspicious_word_count": sum(1 for w in SUSPICIOUS_WORDS if w in url.lower()),
        "is_https": int(parsed.scheme == "https"),
        "uses_shortener": int(any(host.endswith(s) for s in SHORTENER_DOMAINS)),
        "path_token_count": len([p for p in parsed.path.split("/") if p])
    }
    return features

def trace_redirects(url: str, max_hops: int = 6, timeout: float = 5.0) -> list:
    hops = []
    try:
        session = requests.Session()
        r = session.get(url, timeout=timeout, allow_redirects=True)
        for resp in r.history:
            hops.append({"status": resp.status_code, "url": resp.url})
            if len(hops) >= max_hops:
                break
        hops.append({"status": r.status_code, "url": r.url})
    except requests.RequestException as e:
        hops.append({"error": str(e)})
    return hops
