# Novel Studio / 小说创作工作台

A unified fiction-writing skill for **project setup, worldbuilding, outlining, chapter writing, serialization management, review, style polishing, writing training, and reusable style-library workflows**.

一个统一的小说创作技能，覆盖：**立项、设定、大纲、章节写作、连载管理、审校、润色、写作学习训练，以及可复用的风格库工作流**。

It is not a black-box tool that “writes the whole novel for you”. It is a more stable workspace for long-form fiction projects:

它不是“自动替你写完整本小说”的黑箱工具，而是一个更适合长期项目的创作工作台：

- clarify constraints before writing / 写之前帮助收束约束与方向
- stabilize structure, character, pacing, and hooks during drafting / 写的时候稳住结构、人物、节奏和钩子
- support review, summaries, tracking, and style cleanup after drafting / 写完后支持审校、摘要、状态追踪与文风整理
- reduce setting drift, forgotten foreshadowing, and pacing collapse in long serial projects / 在长篇推进中降低设定漂移、伏笔遗失和节奏散掉的风险

---

## Core Capabilities / 核心能力

### 1. Project Setup / 项目初始化
- new project setup / 新书立项
- project skeleton creation / 项目骨架创建
- foundational file structure / 基础文件结构搭建

### 2. Worldbuilding & Planning / 设定与规划
- world, character, faction, and power-system design / 世界观、角色、势力与力量体系
- volume outline, chapter outline, timeline, and foreshadowing / 分卷大纲、章节大纲、时间线与伏笔表
- long-form structure constraints / 长篇结构约束与状态管理

### 3. Chapter Writing / 章节写作
- write, continue, or rewrite chapters / 单章写作、续写、重写
- pre-write analysis → task sheet → draft → self-check → polish → metadata update / 预写分析 → 写作任务书 → 初稿 → 自检 → 润色 → 元数据更新
- a more stable chapter-level workflow / 更稳定的章节级创作流程

### 4. Serialization Management / 连载管理
- main plot / relationship / worldbuilding rhythm checks / 主线、感情线、世界观线的节奏约束
- pacing debt detection / 节奏债务检查
- chapter summaries and project tracking / 连载状态跟踪与章节摘要

### 5. Review & Polishing / 审校与润色
- logic review / 逻辑检查
- characterization review / 人设检查
- timeline review / 时间线检查
- style polish and de-AI editing / 文风优化与去 AI 味

### 6. Learning Mode (v0.2.0) / 学习模式（v0.2.0）
- diagnose writing weaknesses / 诊断当前写作短板
- create staged training plans / 制定分阶段训练计划
- turn advice into project tasks / 把建议反打到项目里
- close the loop: learn → apply → review / 建立“学习 → 应用 → 复盘”闭环

### 7. Structured Templates (v0.2.0) / 结构化模板（v0.2.0）
- character three-table template / 角色三表模板
- chapter progression checklist / 章节推进检查表
- motivation change tracking / 角色动机变化表

### 8. Style Library Workflow (v0.3.0) / 风格库工作流（v0.3.0）
- extract reusable style cards / 提炼可复用风格卡
- convert style studies into prompts / 将风格研究转成可执行提示词
- store style assets under references / 把风格资产沉淀到 references 中
- support sub-cards such as dialogue-only profiles / 支持对白专项等子风格卡

---

## v0.3.0 Highlights / v0.3.0 更新亮点

This release focuses on:

本次版本重点升级：

- **Style Library Workflow / 风格库工作流**
- **Reusable style cards and prompt-ready references / 可复用风格卡与可直接调用的提示词参考**
- **A Three-Body style profile plus dialogue-focused sub-profile / 《三体》总风格卡与对白专项卡**

See details in / 详细说明见：
- [`RELEASE_NOTES_v0.3.0.md`](./RELEASE_NOTES_v0.3.0.md)

---

## Repository Structure / 仓库结构

- [`SKILL.md`](./SKILL.md) — main skill specification / 技能主说明与工作模式
- [`references/`](./references/) — references and templates / 参考文档与模板
- [`novel-studio.skill`](./novel-studio.skill) — distributable skill package / 可分发技能包
- [`_meta.json`](./_meta.json) — metadata / 元信息
- [`RELEASE_NOTES_v0.3.0.md`](./RELEASE_NOTES_v0.3.0.md) — release notes / 本次更新说明

---

## Best Fit / 适用场景

Best for:

更适合：

- long-form novels and webnovels / 长篇小说与网文连载
- projects that need stable settings, timelines, and character tracking / 需要长期维护设定、时间线与角色状态的项目
- writers who want a more stable workflow / 想把写作流程做得更稳的人
- writers who want to train while writing / 想把“学习写作”直接落回作品的人

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
2. Check the relevant docs in [`references/`](./references/) / 按任务类型查看 `references/`
3. Use [`novel-studio.skill`](./novel-studio.skill) for installation or distribution / 需要安装或分发时使用 `novel-studio.skill`

---

## Current Version / 当前版本

- **v0.3.0**
- Repository / 仓库：<https://github.com/oaidea/novel-studio>
