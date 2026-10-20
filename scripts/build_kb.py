#!/usr/bin/env python3
"""把 runningwritings 语料整理为结构化知识库
输出：
  - 00-索引.md            全站文章索引（按年份/主题）
  - topics/*.md           按主题聚合的摘录
  - 01-核心方法论.md       核心方法论文档
"""
import json, glob, os, re, collections

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "kb")
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(OUT, "topics"), exist_ok=True)

def load():
    arts = []
    for f in sorted(glob.glob(os.path.join(BASE, "articles", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        d["file"] = os.path.basename(f)
        ym = re.match(r"(\d{4})-(\d{2})-", d["file"])
        d["year"] = int(ym.group(1)) if ym else 0
        d["month"] = ym.group(2) if ym else ""
        arts.append(d)
    return sorted(arts, key=lambda a: (a["year"], a["month"]), reverse=True)

# 主题分类：关键词 -> 主题名
TOPICS = {
    "百分比/全谱系训练(Canova)": [
        r"percentage-based", r"full-spectrum", r"canova", r"百分比", r"race pace",
        r"意大利", r"italian school", r"specific endurance", r"special block",
    ],
    "阈值与乳酸(LT1/LT2)": [
        r"\bLT1\b", r"\bLT2\b", r"lactate", r"threshold", r"阈值", r"zone 2",
        r"aerobic threshold", r"anaerobic threshold", r"临界速度", r"critical speed",
        r"critical velocity", r"双阈值", r"double threshold",
    ],
    "马拉松训练原理": [
        r"marathon", r"马拉松", r"periodization", r"周期", r"taper", r"减量",
        r"base training", r"基础期", r"生理韧性", r"physiological resilience",
        r"fueling", r"补给", r"carbo-loading", r"carbon load", r"glycogen",
    ],
    "损伤与康复": [
        r"injur", r"损伤", r"pain", r"痛", r"tendon", r"腱", r"stress fracture",
        r"应力性骨折", r"plantar", r"足底", r"achilles", r"跟腱", r"shin splint",
        r"髂胫束", r"iliotibial", r"it band", r"eccentric", r"离心", r"rehab",
        r"bone stress", r"metatarsal", r"跖骨", r"tibial",
    ],
    "生物力学与跑姿": [
        r"biomechanic", r"生物力学", r"cadence", r"步频", r"ground contact",
        r"冲击", r"impact", r"stiffness", r"刚度", r"跑姿", r"gait", r"stride",
        r"shoe", r"鞋", r"spike", r"super spike", r"碳板", r"stryd", r"rundynamics",
    ],
    "心率与监测": [
        r"heart rate", r"心率", r"\bHR\b", r"hrv", r"wearable", r"可穿戴",
        r"cadence lock", r"gps", r"altitude", r"海拔", r"heat", r"高温",
        r"weather", r"headwind", r"tailwind", r"风",
    ],
    "训练计划设计": [
        r"training plan", r"训练计划", r"interval", r"间歇", r"warm-up", r"热身",
        r"cool-down", r"放松", r"strides", r"加速跑", r"plyometric", r"超等长",
        r"strength", r"力量", r"recovery", r"恢复", r"workout", r"课",
    ],
    "比赛策略与心理": [
        r"race plan", r"比赛", r"pacing", r"配速", r"mental", r"心理",
        r"goal", r"目标", r"psycholog", r"tactics", r"策略",
    ],
    "高原/环境适应": [
        r"altitude", r"高原", r"heat", r"高温", r"humidity", r"湿",
    ],
    "青少年与运动科学": [
        r"high school", r"青少年", r"young athlete", r"specialization",
        r"reds", r"growth", r"发育",
    ],
}

def classify(a):
    t = (a["title"] + "\n" + a["body"][:6000]).lower()
    hits = []
    for topic, pats in TOPICS.items():
        score = sum(1 for p in pats if re.search(p, t, re.I))
        if score:
            hits.append((score, topic))
    hits.sort(reverse=True)
    return [h[1] for h in hits] or ["其他"]

def summarize(a, n=3):
    """从正文抽取开头若干段作为摘要"""
    paras = [p.strip() for p in a["body"].split("\n") if len(p.strip()) > 60]
    return paras[:n]

def main():
    arts = load()
    print(f"载入 {len(arts)} 篇")

    # 1) 全站索引
    lines = ["# runningwritings.com 全站文章索引\n",
             f"共 **{len(arts)}** 篇，覆盖 {min(a['year'] for a in arts)}–{max(a['year'] for a in arts)} 年。",
             "本索引仅含正文，已剔除文末参考链接与相关文章区块。\n"]
    by_year = collections.defaultdict(list)
    for a in arts:
        by_year[a["year"]].append(a)
    for y in sorted(by_year, reverse=True):
        lines.append(f"\n## {y} 年（{len(by_year[y])} 篇）\n")
        for a in by_year[y]:
            tg = "、".join(classify(a)[:2])
            lines.append(f"- [{a['title']}]({a['url']})  \n  `{tg}` · {len(a['body']):,} 字")
    open(os.path.join(OUT, "00-索引.md"), "w", encoding="utf-8").write("\n".join(lines))

    # 2) 主题聚合
    topic_map = collections.defaultdict(list)
    for a in arts:
        for t in classify(a):
            topic_map[t].append(a)

    for topic, items in sorted(topic_map.items(), key=lambda x: -len(x[1])):
        out = [f"# {topic}\n", f"共 {len(items)} 篇\n"]
        for a in items:
            out.append(f"\n---\n\n## {a['title']}\n")
            out.append(f"- 来源：{a['url']}")
            out.append(f"- 年份：{a['year']}-{a['month']} · 正文 {len(a['body']):,} 字\n")
            for p in summarize(a, 2):
                out.append(f"> {p[:400]}\n")
            out.append(f"\n<details><summary>展开全文</summary>\n\n{a['body']}\n\n</details>\n")
        safe = re.sub(r"[/\\:*?\"<>|]", "_", topic)
        open(os.path.join(OUT, "topics", f"{safe}.md"), "w", encoding="utf-8").write("\n".join(out))

    # 3) 总库
    allf = ["# runningwritings.com 知识库全文合辑\n",
            f"共 {len(arts)} 篇，{sum(len(a['body']) for a in arts):,} 字。\n"]
    for a in arts:
        allf.append(f"\n\n# {a['title']}\n\n来源：{a['url']}\n\n{a['body']}\n")
    open(os.path.join(OUT, "02-全文合辑.md"), "w", encoding="utf-8").write("".join(allf))

    print("主题分布：")
    for t, i in sorted(topic_map.items(), key=lambda x: -len(x[1])):
        print(f"  {len(i):>3}  {t}")
    print(f"\n输出目录: {OUT}")

if __name__ == "__main__":
    main()
