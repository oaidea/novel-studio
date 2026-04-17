# Novel Studio / 小说创作工作台

A unified long-form fiction studio for **project governance, packet-first chapter writing, project-level style modeling, chapter startup workflows, serialization management, review, and low-token context orchestration**.

一个统一的长篇小说创作工作台，覆盖：**项目治理、packet-first 单章写作、项目级母风格建模、章节启动工作流、连载管理、审校，以及低 token 上下文装载编排**。

It is not a black-box tool that “writes the whole novel for you”. It is a structured fiction operating system for long-running projects:

它不是“自动替你写完整本小说”的黑箱工具，而是一个更像操作系统的长期创作工作台：

- structure the project before writing / 写之前先把项目结构搭稳
- stabilize chapter inputs with packet, summary, style overlay, and object state summary / 写的时候用 packet、summary、style overlay、对象状态摘要稳住输入
- reduce reliance on full chapter rereads / 降低对前文章节全文反复回读的依赖
- keep project style, object state, and workflow emergence aligned / 让项目母风格、对象状态和章节工作流始终对齐

---

## Core Capabilities / 核心能力

### 1. Project Governance / 项目治理
- project skeleton creation / 项目骨架创建
- core/world/subsettings layering / 总设定、规则层、子设定分层
- chapter flow vs brainstorm flow separation / 正文流与发散流分离
- entrypoint layering: README / project-notes / nav / 入口层级分工
- naming conventions and card systems / 命名规范与卡片系统

### 2. Packet-First Chapter Writing / Packet-First 单章写作
- chapter startup packet workflow / 章节启动 packet 工作流
- summary-first continuation / 先摘要、后续写
- object state summaries / 对象状态摘要
- lower-token chapter input packs / 低 token 单章输入包
- fulltext escalation only when necessary / 仅在必要时升级回读全文

### 3. Project Style Model / 项目级风格模型
- mother-style card generation / 项目母风格卡生成
- style extraction from published chapters first / 已发布章节优先的风格提取
- chapter style overlay / 单章风格调用说明
- style consistency checking / 风格一致性检查

### 4. Serialization Management / 连载管理
- chapter summaries and project state / 连载状态跟踪与章节摘要
- pacing, hook, and continuity checks / 节奏、钩子、承接检查
- active indexes for low-token retrieval / 面向低 token 的活动索引

### 5. Review & Polishing / 审校与润色
- logic review / 逻辑检查
- characterization review / 人设检查
- timeline review / 时间线检查
- style polish and de-AI editing / 文风优化与去 AI 味

### 6. Semi-Automation / 半自动工作流
- init workflow / 初始化工作流
- chapter startup / 章节启动
- style-full / 风格链接入
- chapter-full / 章节可写状态报告
- writeback / refresh / style check / 回写、刷新与风格检查
- workflow runner / 统一 workflow 入口

---

## v0.6.9 Highlights / v0.6.9 更新亮点

Highlights / 亮点：
- **Chapter Dependency Graph / 章节依赖图谱**：`build_chapter_deps.py` 自动从 packet/summary/章节文本中提取九种依赖关系（foreshadow、callback、character-intro、space-return 等），维护 `chapter-deps.json`，防止伏笔断线
- **Packet-First Writing**：chapter packet、summary-first、对象状态摘要、最小输入包
- **Workflow Orchestration**：startup / style-full / chapter-full / deps / deps-all / refresh / writeback / full 模式
- **Input Pack Tiers**：模型极简版 / 模型标准版 / 人工审阅版输入包

---

## Repository Structure / 仓库结构

- [`SKILL.md`](./SKILL.md) — main skill specification / 技能主说明与工作模式
- [`references/`](./references/) — references, strategies, templates / 参考文档、策略与模板
- [`scripts/`](./scripts/) — workflow scaffolds and utilities / 工作流脚手架与工具脚本
- [`novel-studio.skill`](./novel-studio.skill) — distributable skill package / 可分发技能包
- [`_meta.json`](./_meta.json) — metadata / 元信息

---

## Best Fit / 适用场景

Best for:

更适合：

- long-form novels and webnovels / 长篇小说与网文连载
- projects that need stable settings, style, and object tracking / 需要长期维护设定、风格与对象状态的项目
- writers who want low-token chapter workflows / 想建立低 token 单章创作流程的人
- writers who want project-level style consistency / 想稳住整部作品母风格的人

---

## Not the Best Fit / 不太适合的场景

This is probably overkill for:

以下场景未必需要它：

- short non-fiction copy / 非小说类短文案
- one-off micro rewrites / 一次性极短文本改写
- lightweight writing tasks with no project structure / 完全不需要项目管理的轻量写作

---

## Quick Start / 快速开始

1. Read [`SKILL.md`](./SKILL.md) first / 先读 `SKILL.md`
2. Use [`references/`](./references/) to find governance, packet-first, style, and workflow docs / 从 `references/` 里查治理、packet-first、风格与工作流文档
3. Use [`scripts/`](./scripts/) to initialize or run workflows / 用 `scripts/` 初始化项目或运行工作流
4. Use [`novel-studio.skill`](./novel-studio.skill) for installation or distribution / 需要安装或分发时使用 `novel-studio.skill`

---

## Current Version / 当前版本

- **v0.6.9**
- Repository / 仓库：<https://github.com/oaidea/novel-studio>
