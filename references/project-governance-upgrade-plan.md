# Novel Studio 升级状态说明（基于《凡尘箓》整理经验）

> 说明：本文件原本是升级规划草案。
> 截至当前版本，其中多数核心升级已完成；因此这里不再把它当“待做清单”，而改为：
> 1. 记录已经吸收进 `novel-studio` 的能力
> 2. 标出仍可继续增强的增量方向

---

## 一、已完成吸收的核心能力

### 1. 项目治理能力已正式纳入
当前 `novel-studio` 已不再只是：
- 立项
- 设定
- 规划
- 章节写作
- 连载管理
- 审校
- 润色
- 学习
- 风格库

还已正式纳入：
- **项目治理 / 仓库结构治理 / 卡片化管理能力**

对应落点包括：
- `SKILL.md` 中的 **项目治理模式**
- `references/project-governance.md`
- `references/entrypoint-layering.md`
- `references/project-init-template.md`
- `references/project-migration-flat-to-layered.md`

### 2. 骨架与脚手架已升级为 layered / packet-first
当前标准骨架已明确支持：
- `README.md / docs/project-notes.md / nav/` 三层入口
- `chapters/` 与 `brainstorm/` 分流
- `settings/core / world / subsettings` 分层
- `events/`、`items/`、`project-style-card.md`
- `.novel-studio/` 作为结构化工作内核

对应落点包括：
- `references/project-init-template.md`
- `references/templates/project-skeleton-template.md`
- `scripts/init_novel_project.py`

### 3. 状态结构已升级
当前推荐状态结构已从极简 draft 升级为更接近实战项目的版本：
- `references/state-json-schema.md`
- `references/chapter-meta-schema.md`

### 4. 治理审计链路已补齐
当前已具备：
- `scripts/governance_audit.py`
- `scripts/workflow_runner.py ... doctor`

用于发现：
- 目录缺失
- state/meta 漏项
- 章节文件未登记进 meta
- 入口文档引用失效
- 常见治理漂移

---

## 二、这轮升级真正改变了什么

升级后的 `novel-studio` 不再只是：
- 会写小说
- 会立项
- 会做设定

而是进一步成为：

> **一个能管理小说项目结构、保持设定稳定、追踪对象变化、支持长期连载维护，并能自查治理漂移的创作工作台。**

---

## 三、仍值得继续增强的方向

### 1. 更深的 doctor / lint 能力
当前治理审计已经可用，但仍偏轻量。
未来可继续增强：
- naming lint
- deeper link lint
- packet / summary / meta consistency checks
- stale index detection

### 2. 回归测试 / fixture
当前脚手架、模板、审计器已经形成闭环。
下一步可继续补：
- 最小样板工程
- 脚本回归测试
- 文档与脚手架一致性检查

### 3. 自动迁移辅助
当前已有迁移文档，但还没有真正的迁移助手脚本。
未来可考虑：
- old flat file mapping helper
- nav / docs rewrite assistant
- legacy archive helper

---

## 四、一句话结论

> 《凡尘箓》这轮整理沉淀出的“项目治理能力”已经不再只是经验草案，而是已经进入 `novel-studio` 的正式骨架、文档与脚本链路。 
