# novel-studio

`novel-studio` 是一个统一小说创作技能，面向**长篇小说、网文连载、结构化章节写作、审稿与润色**场景。它把原本分散的几类能力整合成一个入口：立项、设定、大纲、单章写作、连载管理、章节审校、文风优化，都可以走同一个技能完成。

`novel-studio` is a unified writing skill for **long-form fiction, webnovels, structured chapter drafting, review, and polishing**. It combines several writing-related workflows into a single entry point: project setup, worldbuilding, outlining, chapter drafting, serial management, chapter review, and style refinement.

当前版本 / Current version: **v0.1.0**

---

## 简介 / Overview

它不是替你“自动写完小说”，而是给创作过程提供一个更稳定的工作台：

- 写之前能收束约束
- 写的时候能稳住结构
- 写完后能做审校和摘要
- 长篇推进时不容易忘设定、丢伏笔、散节奏

It is not designed to “auto-write a whole novel” for you. Its purpose is to provide a more stable workspace for fiction writing:

- gather constraints before drafting
- keep structure stable during writing
- support review and summary after drafting
- reduce setting drift, lost foreshadowing, and pacing collapse in long-form work

---

## 当前支持 / Core features

### 1. 项目初始化 / Project setup
支持建立小说项目骨架，包括：

- 故事主线 / story premise
- 世界观设定 / worldbuilding
- 角色档案 / character sheets
- 力量体系 / power system
- 分卷大纲 / volume outline
- 章节大纲 / chapter outline
- 时间线 / timeline
- 伏笔与回收 / foreshadowing tracker
- 状态追踪 / continuity tracking
- 当前进度 / progress tracking

### 2. 章节级结构化写作 / Structured chapter drafting
内置章节工作流：

**预写分析 → 任务书 → 初稿 → 自检 → 润色 → 元数据更新**

Built-in chapter workflow:

**pre-write analysis → task brief → draft → self-check → polish → metadata update**

适合 / Useful for:
- 单章创作 / writing a single chapter
- 重写弱章 / rewriting a weak chapter
- 卡文时拆解任务 / breaking writer’s block into smaller tasks
- 降低长篇断层和失控 / keeping long-form writing from drifting

### 3. 长篇连载管理 / Long-form serial management
内置简化三线节奏模型：

- **Quest** — 主线推进 / main plot progression
- **Fire** — 关系与情感推进 / relationship and emotional progression
- **Constellation** — 世界观扩展 / worldbuilding and setting expansion

用来减少这些常见问题 / Helps reduce:
- 主线太久不动 / main plot stalling too long
- 感情线长期失踪 / relationship lines disappearing
- 世界观只提不落地 / setting being mentioned but never grounded

### 4. 章节审核 / Chapter review
支持检查 / Review checks include:
- 主线推进 / plot progression
- 冲突强度 / conflict strength
- 时间线 / timeline consistency
- 场景与行动逻辑 / scene and action logic
- 设定一致性 / setting consistency
- 人设稳定性 / character consistency
- 钩子强度 / hook strength
- 节奏债务 / pacing debt
- AI 味 / 解释腔 / AI-ish writing and over-explanation

### 5. 文风优化 / Style refinement
内置去 AI 味的润色方向，重点处理：

- 解释感太重 / over-explained prose
- 结构过于工整 / overly neat structure
- 情绪只说不落地 / emotion told instead of shown
- 抽象词太多 / too much abstraction
- 人物声音不分 / weak character voice
- 句式节奏重复 / repetitive sentence rhythm

---

## 内置参考文件 / Included reference files

- `project-init-template.md` — 项目初始化模板 / fiction project initialization template
- `context-contract.md` — 章节创作合同模板 / chapter writing contract template
- `state-tracking-template.md` — 状态追踪模板 / continuity and state tracking template
- `chapter-review-template.md` — 章节审核报告模板 / chapter review report template
- `chapter-summary-template.md` — 章节摘要与元数据模板 / chapter summary and metadata template
- `genre-profiles.md` — 题材配置 / genre pacing profiles
- `strand-weave.md` — 三线节奏规则 / three-line pacing rules
- `cool-points.md` — 爽点设计指南 / payoff and “cool point” design guide
- `humanize-checklist.md` — 去 AI 味检查清单 / AI-prose cleanup checklist

---

## 适用对象 / Who this is for

适合：
- 在写长篇小说或网文的人
- 想把写作流程做得更稳定的人
- 需要统一管理设定、章节和进度的人

Recommended for:
- writers working on long-form fiction or webnovels
- people who want a more stable chapter workflow
- users who need one repeatable system for outlines, drafting, review, and revision

不适合：
- 普通短文案生成
- 非小说类专业写作
- 依赖外部 API 或复杂脚本的自动化流水线

Not intended for:
- generic short-form copywriting
- non-fiction professional writing workflows
- automation-heavy pipelines depending on external APIs or scripts

---

## 当前状态 / Status

这是一个 **v0.1.0 测试版**。已经可以实际使用，但还没有经过大量不同题材、不同项目的长期回测。

This is a **v0.1.0 test release**. It is already usable, but it has not yet gone through enough real-world testing across many genres and projects.

适合 / Recommended use:
- 小范围试用 / small-scale trial use
- 自己项目内先跑 / personal fiction projects
- 边用边修 / iterative refinement through actual use

不建议 / Not recommended yet:
- 直接当作完全成熟的终版能力描述 / presenting it as a fully mature final workflow
- 不经测试就宣称适配所有写作流派 / claiming universal fit for every writing style

---

## 打包产物 / Package

已提供打包文件 / Packaged release file included:

- `novel-studio.skill`

---

## 后续方向 / Roadmap

后续可能继续补充 / Possible future improvements:

- 更完整的项目状态文件规范 / more complete project state conventions
- 更细的题材差异化配置 / richer genre-specific writing profiles
- 更稳的章节摘要与审核联动 / tighter summary and review linkage
- 基于实战回测的流程收缩与精简 / workflow simplification after real-world testing
- 更适合发布平台的元数据与说明整理 / cleaner publishing metadata and release polish

---

## 仓库 / Repository

GitHub: https://github.com/oaidea/novel-studio
