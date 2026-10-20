# Running Coach · 跑步训练教练专家 · 开发文档

> 本项目沉淀了 **「跑步训练教练专家（run-coach-expert）」** 的开发过程资料：
> 如何把 [runningwritings.com](https://runningwritings.com) 全站正文构建成结构化知识库，
> 以及如何据此蒸馏出一套以 Canova 全谱系训练法为核心的跑步训练方法论。

本仓库**只收录开发性质的资料（非交付产物）**：构建脚本、项目文档、方法论文档。
专家 Agent 本体、知识库成品、个人训练计划与分析报告等交付物不在此仓库内。

---

## 一、这个仓库是什么 / 不是什么

| 类别 | 内容 | 是否在仓库内 |
|---|---|---|
| ✅ 构建脚本 | `scripts/` 下 5 个抓取/清洗/构建脚本 | 是 |
| ✅ 项目文档 | 本 README | 是 |
| ✅ 方法论文档 | `docs/methodology.md`（从全站蒸馏出的训练理论） | 是 |
| ❌ 专家 Agent 本体 | `run-coach-expert/`（WorkBuddy 专家包） | 否（交付产物） |
| ❌ 知识库成品 | `runningwritings-知识库/`（191 篇正文合辑、索引、分主题） | 否（交付产物） |
| ❌ 个人交付物 | 你的 10K 训练计划、近两周数据分析报告等 | 否（个人产物） |

> 即：本仓库告诉你**怎么造出来**，而不包含造出来的最终产品。

---

## 二、知识库构建流程

整条流水线把 runningwritings.com 的 191 篇文章，从网页变成一份干净、可检索的正文语料：

```
runningwritings.com
   │  ① enumerate.py   枚举全站文章 URL（首页翻页 + 各分类归档）
   ▼
urls.json  (191 条链接)
   │  ② fetch_all.py   经 agent-browser 渲染通道逐篇抓取 HTML
   ▼
articles/*.json  (每篇: title / url / body / links / chars)
   │  ③ extract_body.js  精确提取正文、剔除文末参考链接与 Related articles
   ▼
（清洗后的结构化正文）
   │  ④ build_kb.py   按主题分类、生成索引与全文合辑
   ▼
kb/00-索引.md · kb/topics/*.md · kb/02-全文合辑.md
```

### 各脚本职责

| 脚本 | 作用 | 关键说明 |
|---|---|---|
| `enumerate.py` | 枚举文章 URL | 注入 JS 到浏览器，从首页翻页 + 10 个分类归档页收集链接，输出 `urls.json` |
| `fetch_all.py` | 抓取正文 | 调用 `extract_body.js`，带 3 次重试与本地缓存，输出 `articles/*.json` |
| `extract_body.js` | 正文清洗 | 定位 `article .entry-content`，剔除广告/推荐/评论区块，并**精确切除文末 Related articles** |
| `build_kb.py` | 构建知识库 | 按 10 个主题（正则匹配）分类聚合，产出索引、分主题摘录、全文合辑 |
| `fix_one.js` | 单次修正工具 | 针对个别文章残留的 "Related articles" 标题做一次性 DOM 切除 |

> **关于 403 的历史坑**：早期 runningwritings.com 对直连（curl / Playwright / Wayback / 代理）全站返回 403，
> 唯一可用通道是 `agent-browser`（Chrome 渲染）。**截至 2026-10-10 起，该站 403 已解除，curl 直连可正常返回正文**，
> 因此后续重跑流水线时，可把 `fetch_all.py` 中的 `agent-browser open` 换成直接 HTTP 抓取以提速。

---

## 三、依赖与运行

### 依赖
- **Python 3.11+**（运行 `enumerate.py` / `fetch_all.py` / `build_kb.py`）
- **Node.js**（运行 `extract_body.js` 这类注入页面的 JS；若改用服务端 HTML 解析可去掉）
- **agent-browser CLI**（早期绕过 403 的渲染通道；403 解除后可选）

### 运行步骤
```bash
# 1) 枚举全站文章 URL -> urls.json
python3 scripts/enumerate.py

# 2) 抓取并清洗正文 -> articles/*.json
python3 scripts/fetch_all.py

# 3) 构建知识库 -> kb/（索引 + 分主题 + 全文合辑）
python3 scripts/build_kb.py
```

> 脚本均使用「相对自身目录」的路径（`BASE = 脚本所在目录`），在仓库任意位置运行即可，
> 输出（`urls.json` / `articles/` / `kb/`）会落在脚本所在目录下。建议把这些中间产物加入 `.gitignore`。

---

## 四、方法论蒸馏（核心理论）

从全站正文蒸馏出的训练理论，已整理进 [`docs/methodology.md`](docs/methodology.md)，要点包括：

- **Canova 全谱系百分比体系**：以比赛配速为 100%，覆盖 55–65%（轻松）到 107–110%（支持性速度）的完整强度谱系；
- **双阈值训练（Marius Bakken）**：上午长间歇（6–10min，低乳酸）+ 下午短间歇（45-15 / 1min / 200m，高乳酸），间隔 4–5h；
- **入门期（introductory training）**：长期中断后重返，低跑量即新应激，以 effort-based 而非严格配速为主；
- **减量（taper）**：结构化减量平均提升约 2–3% 成绩（Bosquet 2007 Meta 分析）。

---

## 五、专家 Agent 是怎么来的（不在本仓库）

专家包 `run-coach-expert/` 是最终交付物，运行在 WorkBuddy 桌面端，其知识由三层构成：

1. **L0 核心层（最强）**：蒸馏后的方法论直接内嵌进 Agent 提示词，运行即加载，部署即用；
2. **L1 文档层**：`kb/00`、`kb/01` 两份精选笔记，随专家包分发；
3. **L2 语料层**：本仓库构建出的 17MB 全站语料，因体积过大不随包分发，建议挂入 WorkBuddy 资料库（Library）做 RAG 检索。

> 关于 RAG：把 `.md` 放进包 ≠ 自动灌入 Agent 上下文。真正的 RAG 需要「资料库检索工具 + 运行时向量检索 + 注入相关片段」，
> 这部分基础设施需在使用端另行接入。

---

## 六、目录结构

```
running-coach/
├── README.md              # 本文件：项目与构建流程说明
├── LICENSE                # MIT
├── .gitignore
├── scripts/               # 知识库构建流水线
│   ├── enumerate.py       # 枚举文章 URL
│   ├── fetch_all.py       # 抓取正文（带重试/缓存）
│   ├── extract_body.js    # 正文清洗（剔除推荐/相关文章）
│   ├── build_kb.py        # 主题分类 + 索引 + 全文合辑
│   └── fix_one.js         # 单次 DOM 修正工具
└── docs/
    └── methodology.md     # 从全站蒸馏出的训练方法论文档
```

---

## 七、许可

[MIT License](LICENSE)。构建脚本与文档可自由用于非商业的训练研究与人肉知识整理。
注意：runningwritings.com 的文章版权归原作者所有，本仓库不包含其原文，
仅提供**抓取与构建方法**；请遵守该站 robots 与版权政策，勿将原文语料用于商业再分发。
