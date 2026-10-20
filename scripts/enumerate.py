#!/usr/bin/env python3
"""枚举 runningwritings.com 全部文章 URL：翻页 /page/N + 各分类归档"""
import json, os, re, subprocess, time

BASE = os.path.dirname(os.path.abspath(__file__))

COLLECT_JS = """
(() => {
  const all = [...document.querySelectorAll('a[href]')].map(a => a.href.split('#')[0]);
  const posts = [...new Set(all.filter(h => /runningwritings\\.com\\/(19|20)\\d\\d\\/\\d\\d\\/[^\\/]+\\.html$/.test(h)))];
  const nums = [...document.querySelectorAll('a[href*="runningwritings.com/page/"]')]
    .map(a => (a.href.match(/\\/page\\/(\\d+)/) || [])[1]).filter(Boolean).map(Number);
  return JSON.stringify({posts, maxPage: nums.length ? Math.max(...nums) : 0});
})()
"""

def ab(cmd, timeout=150):
    r = subprocess.run(["agent-browser"] + cmd, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "").strip()

def ev(js, timeout=120):
    s = ab(["eval", js], timeout)
    try:
        d = json.loads(s)
        return json.loads(d) if isinstance(d, str) else d
    except Exception:
        return None

def main():
    found = set()
    # 1) 首页 + 翻页
    ab(["open", "https://runningwritings.com/"])
    time.sleep(2)
    first = ev(COLLECT_JS) or {}
    found.update(first.get("posts", []))
    maxp = first.get("maxPage", 0) or 20
    print(f"首页 {len(first.get('posts', []))} 篇，最大页码 {maxp}", flush=True)

    for p in range(2, maxp + 1):
        ab(["open", f"https://runningwritings.com/page/{p}"])
        time.sleep(1.5)
        d = ev(COLLECT_JS) or {}
        new = [u for u in d.get("posts", []) if u not in found]
        found.update(d.get("posts", []))
        m = d.get("maxPage", 0)
        if m > maxp: maxp = m
        print(f"  第 {p} 页: +{len(new)} (累计 {len(found)})", flush=True)
        if not d.get("posts"):
            print("  空页，停止翻页", flush=True)
            break

    # 2) 各分类归档
    cats = ["training","science","biomechanics","injuries","high-school","apps","podcasts","physiology","racing","reviews"]
    for c in cats:
        ab(["open", f"https://runningwritings.com/category/{c}"])
        time.sleep(1.5)
        d = ev(COLLECT_JS) or {}
        new = [u for u in d.get("posts", []) if u not in found]
        found.update(d.get("posts", []))
        print(f"  分类 {c}: +{len(new)} (累计 {len(found)})", flush=True)

    urls = sorted(found, reverse=True)
    json.dump(urls, open(os.path.join(BASE, "urls.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n共枚举 {len(urls)} 篇文章 -> urls.json", flush=True)

if __name__ == "__main__":
    main()
