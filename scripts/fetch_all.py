#!/usr/bin/env python3
"""runningwritings.com 全站正文抓取（经 agent-browser 通道）"""
import json, os, re, subprocess, sys, time, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "articles")
os.makedirs(OUT, exist_ok=True)
EXTRACT = os.path.join(BASE, "extract_body.js")
EXTRACT_JS = open(EXTRACT, encoding="utf-8").read()

def ab_eval(js, timeout=120):
    """在 agent-browser 当前页面执行 JS，返回解析后的对象"""
    r = subprocess.run(["agent-browser", "eval", js], capture_output=True,
                       text=True, timeout=timeout)
    s = (r.stdout or "").strip()
    if not s:
        return None
    try:
        d = json.loads(s)
        if isinstance(d, str):
            d = json.loads(d)
        return d
    except Exception:
        return None

def ab_open(url, timeout=150):
    subprocess.run(["agent-browser", "open", url], capture_output=True,
                   text=True, timeout=timeout)

def slug(url):
    m = re.search(r"/(\d{4})/(\d{2})/([^/]+)\.html$", url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else hashlib.md5(url.encode()).hexdigest()[:12]

def fetch(url):
    sl = slug(url)
    path = os.path.join(OUT, sl + ".json")
    if os.path.exists(path):
        try:
            d = json.load(open(path, encoding="utf-8"))
            if d.get("body") and len(d["body"]) > 500:
                return d, "cached"
        except Exception:
            pass
    for attempt in range(3):
        try:
            ab_open(url)
            d = ab_eval(EXTRACT_JS)
            if d and d.get("body") and len(d["body"]) > 500:
                d["slug"] = sl
                json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                return d, "ok"
        except Exception as e:
            print(f"    attempt {attempt+1} err: {e}", flush=True)
        time.sleep(3)
    return None, "fail"

if __name__ == "__main__":
    urls = json.load(open(os.path.join(BASE, "urls.json"), encoding="utf-8"))
    print(f"共 {len(urls)} 篇待抓取", flush=True)
    ok = fail = 0
    for i, u in enumerate(urls, 1):
        d, st = fetch(u)
        if d:
            ok += 1
            print(f"[{i}/{len(urls)}] {st} {len(d['body']):>6}字  {d['title'][:60]}", flush=True)
        else:
            fail += 1
            print(f"[{i}/{len(urls)}] FAIL {u}", flush=True)
    print(f"\n完成：成功 {ok}，失败 {fail}", flush=True)
