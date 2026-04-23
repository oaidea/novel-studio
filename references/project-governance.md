# Project Governance for Novel Studio

> 基于《凡尘箓》项目整理经验抽象出的通用项目治理规则。
>
> 目标不是只把目录摆整齐，而是让长期连载项目在多轮写作、多次重构、低 token 承接下依然稳定：
> - 入口不打架
> - 设定不乱堆
> - 正文流与发散流不混
> - `.novel-studio/` 真正承担结构化工作内核职责

## 一、适用场景
当小说项目出现以下问题时，启用本规则：
- 文件越堆越乱
- 设定混在正文、脑暴稿、导航稿里
- 人物 / 场景 / 空间 / 事件 / 物件的信息找不到
- 章节推进后，对象变化无记录
- README、工作说明、导航摘要互相打架
- 文件名开始出现“最终版-再改版-v2”式失控
- 项目已经能写，但越写越依赖全文回读而不是结构化上下文
- 文档说一套、目录长成另一套，开始发生治理漂移

## 二、核心治理原则

### 1. 创作流与发散流分离
- `chapters/`：实际创作文本
- `brainstorm/`：结构试探、线索讨论、发散稿

原则：
- 进入正文流的文件放 `chapters/`
- 还在试结构、试钩子、试切法的材料放 `brainstorm/`
- 不要让正文目录承担脑暴垃圾堆功能

### 2. 总设定与子设定分层
- `settings/core/`：总设定 / 总纲 / 上位真相
- `settings/world/`：规则层 / 长线边界 / 不可写穿层
- `settings/subsettings/`：对象层资料

原则：
- 能决定世界底层规则、上一代真相、长线结构的，优先放 `core/` / `world/`
- 落到具体对象与写作承接的，优先放 `subsettings/`

### 3. 对象卡与变化记录分离
对以下对象统一采用：
- 卡片本体：当前稳定状态
- 变化记录：变化过程、章节原因、后续影响

对象范围：
- 人物（`characters/`）
- 关系（`relationships/`）
- 时间（`timeline/`）
- 伏笔（`foreshadowing/`）
- 空间（`spaces/`）
- 场景（`scenes/`）
- 事件（`events/`）
- 物件（`items/`）

其中：
- `events/` 用于追踪“发生了什么、造成了什么后果、后续还会牵动谁”
- `items/` 用于追踪会反复出现、承载信息、会跨章节变化状态的关键物件

### 4. 入口层级统一
- `README.md`：总入口
- `docs/project-notes.md`：工作入口
- `nav/`：快速摘要入口

原则：
- `README.md` 讲“仓库是什么、目录怎么分工、第一次先看哪”
- `docs/project-notes.md` 讲“现在该从哪动手”
- `nav/` 讲“快速回忆项目摘要”

### 5. 导航不代替母设定
`nav/` 只做摘要；若与 `settings/` 冲突，以 `settings/` 为准。
若 `project-notes` 与 `settings + workflow` 冲突，以 `settings + workflow` 为准。

### 6. 状态写在目录，不写在文件名
- 正文流 → `chapters/`
- 发散稿 → `brainstorm/`
- 卡片 → `cards/`
- 变化记录 → `changes/`

原则：
- 少写 `最终版-v2-重修-可发` 这类文件名
- 多用目录状态表达文件角色

### 7. `.novel-studio/` 是结构化工作内核
`.novel-studio/` 不存正文全文，而负责：
- `state.json`：项目当前状态
- `chapter-meta.json`：章节级元数据
- `summaries/`：章节结构化摘要
- `packets/`：chapter packet / style overlay
- `indexes/`：活动对象索引
- `logs/`：工作流报告与审计输出

原则：
- 新章节承接优先依赖 `summary + packet + object summary + indexes`
- 不默认依赖回读上一章全文

### 8. 项目风格卡是第一等对象
建议在 `settings/subsettings/project-style-card.md` 维护项目风格总卡。

用途：
- 给章节 style overlay 提供上位约束
- 给审校 / 去AI味 / 风格一致性检查提供稳定基准
- 防止项目越写越失去母风格

### 9. 定期做治理审计
项目越久越容易发生这些漂移：
- 目录与文档不一致
- `chapter-meta.json` 漏章
- `state.json` 太旧
- `nav/` 引用失效
- 文档还在说旧结构

建议定期运行治理检查，而不是等完全乱掉再收拾。

---

## 三、推荐目录骨架

```text
<project>/
├── README.md
├── docs/
│   ├── README.md
│   └── project-notes.md
├── analysis/
├── chapters/
│   ├── published/
│   ├── candidates/
│   ├── early-drafts/
│   ├── drafts/
│   └── revisions/
├── brainstorm/
├── nav/
├── settings/
│   ├── core/
│   ├── world/
│   └── subsettings/
│       ├── project-style-card.md
│       ├── characters/
│       ├── relationships/
│       ├── timeline/
│       ├── foreshadowing/
│       ├── spaces/
│       ├── scenes/
│       ├── events/
│       └── items/
├── workflow/
└── .novel-studio/
```

---

## 四、推荐治理流程

### Step 1：先诊断问题
先判断当前问题属于哪类：
1. 入口打架
2. 设定乱堆
3. 对象资料缺层
4. 正文流 / 发散流混杂
5. `.novel-studio/` 内核缺失或过时
6. 文档与目录不一致

### Step 2：输出迁移映射
治理旧项目时，先给出：
- 原文件 / 原目录
- 对应的新落点
- 保留 / 迁移 / 归档 / 删除建议

### Step 3：先立目录，再迁内容
不要一边想一边乱搬。
先把目标骨架定住，再逐类迁移：
- chapters
- brainstorm
- settings
- nav
- workflow
- `.novel-studio/`

### Step 4：建立入口层级
确保至少有：
- `README.md`
- `docs/project-notes.md`
- `nav/`

### Step 5：建立 `.novel-studio/` 最小内核
至少有：
- `state.json`
- `chapter-meta.json`
- `summaries/`
- `packets/`
- `indexes/`

### Step 6：补对象层
优先补最常用、最能减轻全文回读依赖的对象：
1. `characters/`
2. `timeline/`
3. `foreshadowing/`
4. `spaces/`
5. `scenes/`
6. `events/`
7. `items/`

### Step 7：跑一次治理审计
建议运行：
```bash
scripts/governance_audit.py <project-dir>
```

用来检查：
- required dirs / files 是否齐
- state/meta 是否存在且字段合理
- 章节文件是否漏记进 `chapter-meta.json`
- 入口文档引用是否失效

---

## 五、什么时候适合跑治理审计

推荐在这些时机跑：
- 项目第一次迁入 novel-studio 结构后
- 大规模整理目录后
- 发布几章后回头检查时
- 感觉项目开始“写着写着越来越乱”时
- 给别人接手 / 给未来自己续写前

---

## 六、升级输出建议
治理一个项目时，优先输出：
1. 问题诊断
2. 新结构建议
3. 迁移映射清单
4. 命名规范
5. 卡片 / 变化记录 / 模板清单
6. 入口层级说明
7. 是否需要补 `.novel-studio/` 内核
8. 是否建议运行治理审计

---

## 七、一句话原则

> 项目治理不是为了好看，而是为了让小说项目在长期创作中继续写得动、找得到、接得住、改得稳。 
