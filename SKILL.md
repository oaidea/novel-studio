---
name: novel-studio
version: 0.3.1
description: 统一小说创作总技能。整合立项、世界观/角色设定、分卷与章节大纲、长篇连载状态管理、结构化章节写作、自检审校、文笔润色、去 AI 味、风格库调用、项目结构治理，以及写作学习训练与模板化输出。
---

# Novel Studio

这是一个统一入口的小说创作总技能，融合以下能力：

- **book-writer**：工程化文件体系与全流程管理
- **webnovel-writer**：长篇连载、防遗忘、防设定漂移、追读力与节奏控制
- **novel-writer-structure**：章节级 6 阶段结构化写作与状态追踪
- **humanizer-zh**：文本去 AI 味、语言自然化、人物语气与节奏优化
- **style-library**：风格参考卡调用，可把拆解过的风格转成创作约束或提示词

原则：**一个入口，按任务切模式；先稳逻辑，再出内容，最后润文风。**

---

## 一、何时使用

当用户出现以下需求时，优先使用本技能：

- 写小说、写网文、开新书、做小说项目
- 搭建世界观、角色、力量体系、设定集
- 设计故事主线、分卷大纲、章节大纲、时间线、伏笔表
- 写某一章、续写下一章、重写一章
- 检查剧情逻辑、人设、时间线、伏笔回收、节奏
- 润色文风、去 AI 味、让人物说话更像人
- 管理长篇项目进度、状态追踪、追读力、章节摘要
- 整理小说仓库结构、分离创作流与发散流、建立卡片系统与变化记录
- 提炼某作者/作品风格，做成可复用风格卡或提示词模板

如果用户只是要一小段文案、非小说文本润色，可不启用本技能。

---

## 二、工作模式选择

先判断当前任务属于哪一类，再进入对应模式：

1. **立项模式**：新建小说/项目初始化
2. **设定模式**：世界观、角色、势力、力量体系、风格规范
3. **规划模式**：故事主线、分卷大纲、章节大纲、时间线、伏笔表
4. **章节模式**：单章写作、续写、重写
5. **连载模式**：长篇状态管理、追读力、节奏债务检查、项目记忆更新
6. **审校模式**：逻辑审查、人设审查、时间线审查、节奏审查
7. **润色模式**：文笔优化、去 AI 痕迹、人物语气差异化
8. **学习模式**：写作能力诊断、训练计划、技巧反打到当前项目
9. **风格库模式**：调用已沉淀的风格参考卡，生成可执行风格约束与 prompt 模板
10. **项目治理模式**：整理小说项目结构、拆分设定层级、建立对象卡、变化记录、命名规范与入口层级

**默认规则：**
- 不跨模式乱跳。
- 若缺少必要输入，先补关键约束，再继续。
- 若用户只要一个章节，不强制完整立项，但仍要补足最小创作约束。
- 若用户要“学习写作 / 提升写作能力 / 制定训练计划”，进入**学习模式**，并要求每轮学习都附带项目内应用任务，避免纯理论空转。
- 若用户要“拆某种写法 / 提炼某作者或某作品风格 / 生成风格模板 / 放进风格库”，进入**风格库模式**。
- 若用户要“整理小说项目 / 清理仓库结构 / 把设定和卡片分层 / 建变化记录 / 统一命名规范 / 做创作工作室逻辑”，进入**项目治理模式**。
- 若用户要“确定章节框架后尽量不回读前文全文 / 用卡片和摘要来写 / 降低 token 消耗”，进入**chapter packet / packet-first 写作策略**。
- 若用户要“先根据上一章来推测下一章会出现的人物、空间、时间、事件，再制定本章目的与框架”，也进入**chapter packet / packet-first 写作策略**。
- 若用户要“为单个小说项目建立统一写作风格卡 / 避免章节风格脱离整部作品”，进入**项目风格卡策略**。

---

## 三、推荐项目结构

长篇项目默认放在：`/root/.openclaw/workspace/novels/<项目名>/`

推荐目录：

```text
novels/<项目名>/
├── README.md                # 项目总入口
├── docs/
│   └── project-notes.md     # 工作入口
├── analysis/                # 读者视角分析、阶段复盘
├── chapters/                # 实际创作文本（published/drafts/candidates）
├── brainstorm/              # 发散讨论、结构试探、未进正文流材料
├── nav/                     # 快速摘要入口
├── settings/
│   ├── core/                # 总设定 / 总纲 / 上位真相
│   ├── world/               # 世界规则 / 长线边界
│   └── subsettings/
│       ├── characters/      # 人物卡 / 人物变化记录 / 模板
│       ├── relationships/   # 关系线
│       ├── timeline/        # 时间线
│       ├── foreshadowing/   # 伏笔
│       ├── spaces/          # 空间卡 / 空间变化记录 / 模板
│       └── scenes/          # 场景卡 / 场景变化记录 / 模板
├── workflow/                # 推进计划、章节进度、设计稿
└── .novel-studio/
    ├── state.json
    ├── chapter-meta.json
    ├── summaries/
    ├── packets/
    ├── indexes/
    └── logs/
```

### 最小可运行集

如果用户不想建全套目录，至少保证：

- `docs/project-notes.md`
- `chapters/`
- `settings/core/`
- `settings/subsettings/characters/`
- `settings/subsettings/timeline/`
- `workflow/`
- `.novel-studio/state.json`

---

## 四、立项模式

当用户说“新建小说 / 开新书 / 建项目”时：

### 先收集最小信息

- 书名
- 题材
- 一句话主线
- 预计篇幅
- 目标风格（偏网文爽感 / 偏文学 / 偏克制 / 偏热血）

### 然后创建项目骨架

至少创建：

- `README.md`
- `docs/project-notes.md`
- `chapters/`
- `brainstorm/`
- `nav/`
- `settings/core/`
- `settings/world/`
- `settings/subsettings/characters/`
- `settings/subsettings/relationships/`
- `settings/subsettings/timeline/`
- `settings/subsettings/foreshadowing/`
- `workflow/`
- `.novel-studio/state.json`

### 立项输出内容

应包含：

1. 核心题材判断
2. 主线冲突一句话
3. 初始角色列表
4. 建议的卷结构
5. 下一步待确认项

如需按标准工作室结构初始化项目，优先参考：
- `references/templates/project-skeleton-template.md`

---

## 五、设定与规划模式

### 设定模式必须优先稳住的内容

1. **故事主线**：主角要什么、阻力是什么、代价是什么
2. **世界观与规则**：哪些事能发生，哪些不能发生
3. **角色档案**：动机、能力、关系、红线
4. **写作风格**：人称、语气、节奏、描写密度

### 规划模式输出顺序

1. 分卷大纲
2. 章节大纲
3. 时间线
4. 伏笔与回收
5. 当前进度

### 规划硬规则

- **大纲即法律**：章节不能随意背离已确认大纲
- **设定即物理**：能力、地理、时间、人设必须自洽
- **新发明必须入库**：新增角色/物品/地点/组织后要写回对应文件
- **创作流与发散流分离**：能直接参与定稿的进 `chapters/`，仍在试结构或试切法的进 `brainstorm/`
- **对象卡与变化记录分离**：人物 / 空间 / 场景写“当前状态”和“变化过程”必须分文件管理

---

## 六、章节模式（核心）

写单章时，强制使用以下流程。

### 阶段1：预写分析

写之前先确认：

- 本章目标
- 本章阻力
- 本章代价
- 上章承接点
- 本章结束状态
- 本章必须处理的伏笔
- 时间/地点/人物状态是否连贯

若项目较完整，优先读取：

- `07-章节大纲.md`
- `08-时间线.md`
- `11-状态追踪.md`
- `03-角色档案.md`
- 上一章正文或摘要

### 阶段2：写作任务书

输出简版任务书，至少包括：

1. 本章核心冲突
2. 必须完成事项
3. 不允许发生的事
4. 出场角色与动机
5. 场景约束
6. 本章钩子类型

如果用户希望后续写作尽量不依赖前文全文，或该章已经进入长期维护状态，则额外生成：
- `chapter packet`（参考 `references/chapter-packet-architecture.md` 与 `references/templates/chapter-packet-template.md`）
- 上一章最小承接摘要（参考 `references/templates/chapter-summary-template-packet-first.md`）
- 若时间推进复杂，再补时间锚点（参考 `references/templates/timeline-anchor-template.md`）

### 阶段3：初稿生成

要求：

- 直接写场景，不写“本章讲了什么”
- 每个场景至少包含：环境锚点、动作/对话、情绪节拍、信息推进
- 章末必须留钩子
- 默认一章只写一章，等用户确认后再继续下一章

### 阶段4：自检

至少检查：

- 时间线是否顺
- 人设是否稳
- 伏笔是否推进或标注延期
- 情绪是否自然
- 场景切换是否清楚
- 是否有无因果硬拐
- 是否有越级能力/吃设定

### 阶段5：文笔润色

重点优化：

- 对话区分度
- 动词精准度
- 形容词克制
- 感官描写是否服务情绪
- 避免解释式写法
- 尽量用动作、停顿、细节承载情绪

### 阶段6：元数据更新

如果用户要求维护项目文件，则同步更新：

- `11-状态追踪.md`
- `10-伏笔与回收.md`
- `12-当前进度.md`
- `.novel-studio/state.json`
- `.novel-studio/chapter-meta.json`
- `.novel-studio/summaries/ch_XXXX.md`
- 若采用 packet-first 策略，再同步更新该章 `chapter packet`
- 若本章推进了关键事件，再同步更新事件卡 / 事件变化记录
- 若项目已进入结构化维护，再同步更新 `.novel-studio/indexes/` 中的活动索引

---

## 七、项目治理模式（Project Governance Mode）

当用户说：
- 整理小说项目
- 清理仓库结构
- 拆分设定层级
- 分离正文与脑暴稿
- 建人物卡 / 空间卡 / 场景卡
- 建 change log / 变化记录
- 统一命名规范
- 统一 README / project-notes / nav 的入口层级

进入本模式。

### 目标

不是直接写正文，而是让小说项目本身变得：
- 可维护
- 可导航
- 可持续扩展
- 不容易设定漂移

### 核心规则

1. **入口分层**
   - `README.md`：总入口
   - `docs/project-notes.md`：工作入口
   - `nav/`：快速摘要入口

2. **设定分层**
   - `settings/core/`：总设定 / 上位真相 / 总纲
   - `settings/world/`：规则层 / 长线边界
   - `settings/subsettings/`：人物、关系、时间线、伏笔、空间、场景等子设定

3. **创作流分离**
   - `chapters/`：实际创作文本
   - `brainstorm/`：发散思维、试探材料、线索讨论

4. **对象卡与变化分离**
   对以下对象统一采用：
   - 卡片本体：记录当前稳定状态
   - 变化记录：记录章节推动下的变化过程

   对象范围：
   - 人物
   - 空间
   - 场景

5. **命名规范**
   - 文件名写“对象是什么”，状态写在目录层，不写在文件名里
   - 默认 kebab-case
   - 中文名仅保留给少量总纲类 / 报告类文件

### 推荐参考文件
- `references/project-governance.md`
- `references/card-system.md`
- `references/naming-conventions.md`
- `references/entrypoint-layering.md`
- `references/chapter-packet-architecture.md`
- `references/packet-first-chapter-workflow.md`
- `references/packet-first-execution-checklist.md`
- `references/fulltext-escalation-policy.md`
- `references/novel-studio-internal-structure.md`
- `references/state-json-schema.md`
- `references/chapter-meta-schema.md`
- `references/active-index-templates.md`
- `references/semi-automation-plan.md`
- `references/automation-expansion-plan.md`
- `references/minimal-workflow-chain.md`
- `references/workflow-demo.md`
- `references/scripts-index.md`
- `references/event-card-system.md`
- `references/templates/project-skeleton-template.md`
- `references/templates/chapter-packet-template.md`
- `references/templates/chapter-summary-template-packet-first.md`
- `references/templates/timeline-anchor-template.md`
- `references/templates/chapter-startup-checklist-template.md`
- `references/templates/chapter-writeback-checklist-template.md`
- `references/templates/character-card-template.md`
- `references/templates/character-change-log-template.md`
- `references/templates/space-card-template.md`
- `references/templates/space-change-log-template.md`
- `references/templates/scene-card-template.md`
- `references/templates/scene-change-log-template.md`
- `references/templates/event-card-template.md`
- `references/templates/event-change-log-template.md`

### 推荐输出

1. 基于上一章摘要预测本章依赖对象（人物 / 空间 / 时间 / 事件 / 伏笔）
2. 明确本章的人物目的 / 事件目的 / 空间目的 / 时间目的 / 结构目的
3. 产出本章框架
4. 生成 chapter packet
5. 列出本章预计会改动哪些人物卡 / 时间锚点 / 事件卡 / 空间卡 / 场景卡 / 伏笔记录
6. 如项目已进入长期维护，再明确 `.novel-studio/packets/`、`summaries/`、`indexes/` 将如何更新
7. 必要时附上 `chapter startup checklist` 与 `chapter writeback checklist`
8. 若用户允许，再进入正文生成

### 可选脚本入口
- `scripts/init_novel_project.py`：初始化 packet-first 项目骨架
- `scripts/chapter_startup.py`：为新章节生成 packet 与启动清单骨架
- `scripts/writeback_sync.py`：为章节回写生成 checklist scaffold
- `scripts/index_refresh.py`：初始化 / 刷新活动索引 scaffold
- `scripts/style_check.py`：为单章生成风格一致性检查 scaffold
- `scripts/workflow_runner.py`：串行触发最小 workflow chain（支持 startup / style / style-full / writeback / refresh / full 模式）

---

## 十、项目风格卡策略

当用户说：
- 给这本书定写作风格
- 做项目级风格卡
- 不要让每章自己长风格
- 让章节风格从属于整部小说
- 做单个小说项目的风格基线

进入本策略。

### 核心原则
1. 先定义**项目级风格卡**
2. 每章默认继承项目母风格
3. 单章只允许做任务型局部偏移
4. 写后检查是否仍在项目风格基线内

### 推荐参考文件
- `references/project-style-model.md`
- `references/project-style-generation.md`
- `references/project-style-extraction.md`
- `references/style-consistency-checklist.md`
- `references/style-automation-plan.md`
- `references/templates/project-style-card-template.md`
- `references/templates/chapter-style-overlay-template.md`
- `references/templates/style-generation-template.md`

### 推荐输出
1. 项目母风格定义
2. 章节风格调用规则
3. 本章允许的局部风格偏移
4. 写后风格一致性检查
5. 若用户要求“一键复刻”或“从已有章节提纯”，则额外输出母风格生成结果
6. 若用户允许，再生成项目风格卡 scaffold 或章节风格调用 scaffold

---

## 十一、学习模式（训练模式）

当用户说“我想学写作 / 帮我做写作学习计划 / 我现在最该补什么 / 带我练网文写作”时，进入本模式。

### 目标

不是泛泛讲技巧，而是：

1. 诊断当前作品最该补的 1-3 个能力
2. 给出分阶段训练路径
3. 为每个训练主题安排一个**项目内应用任务**
4. 做到“学 → 用 → 复盘”闭环

### 推荐输出结构

1. 当前问题诊断
2. 本轮训练目标
3. 训练要点
4. 项目内应用任务
5. 复盘标准

### 学习模式硬规则

- 不要一次铺太多训练主题，优先最短板。
- 不要只讲抽象理论，必须回到用户正在写的作品。
- 不要让学习模式替代创作；必要时引导切回规划 / 章节 / 审校模式落地。

需要时，读取：`references/writing-study-plan.md`

---

## 九、风格库模式

当用户说“提炼某种风格 / 拆某作者写法 / 生成风格卡 / 做成提示词模板 / 存到风格库”时，进入本模式。

### 目标

不是泛泛评价某作品“写得好”，而是沉淀成可复用的创作资产：

1. 提炼风格总纲
2. 拆出叙事骨架、语言气质、对话机制、设定展开方式
3. 标出适用场景与误用风险
4. 生成可直接调用的简版提示词或约束模板
5. 写入 `references/` 下的风格库文件

### 推荐输出结构

1. 风格定义
2. 适用题材
3. 叙事方式
4. 对话方式
5. 语言特征
6. 常见误用
7. 可执行规则
8. 简版 prompt 模板

### 风格库模式硬规则

- 不做“像某作者原文一样”的逐句摹写。
- 提炼方法，不复写表达。
- 风格卡必须能转化为创作约束，而不只是评论。
- 若涉及已存在风格卡，优先增补或拆分子卡，而不是无序重复造文件。

需要时，优先读取：
- `references/style-library-index.md`
- 相关风格卡文件

---

## 十、连载模式：长篇防遗忘机制

### 三条叙事线（Strand Weave）

- **Quest（主线）**：约 60%
- **Fire（感情/关系）**：约 20%
- **Constellation（世界观/设定扩展）**：约 20%

### 节奏红线

- Quest 连续不超过 5 章无推进
- Fire 断档不超过 10 章
- Constellation 断档不超过 15 章
- 过渡章连续不超过 2 章

### 追读力债务

若某条线断档过久，后续章节需优先偿还：

- Quest 债务：下一章必须强推进主线
- Fire 债务：安排关系互动或情感波动
- Constellation 债务：补世界观/势力/设定落地

### 爽点管理（网文向）

参考 `references/cool-points.md`：

- 装逼打脸
- 扮猪吃虎
- 越级反杀
- 身份揭晓
- 资源获取
- 团战荣耀
- 认知碾压

不要重复同一种爽点模板；爽点要有铺垫、有见证、有代价。

---

## 十一、审校模式

当用户说“检查这一章 / 看看有没问题 / 审核大纲”时：

从以下维度审：

1. **逻辑一致性**：设定、战力、时间、地理
2. **角色一致性**：动机、语气、行为边界
3. **节奏结构**：冲突、推进、兑现、钩子
4. **伏笔管理**：有没有只埋不收、该提不提
5. **追读力**：章末是否能把人带到下一章
6. **语言质量**：是否有解释腔、重复句式、AI 味

输出建议优先分为：

- 必修问题（不改会伤结构）
- 建议优化（改了会更顺）
- 可选强化（提升爽感/质感）

---

## 十二、润色模式（含去 AI 味）

当用户要求“润色 / 改自然点 / 去 AI 味 / 更像人写的”时：

### 必查问题

- 填充短语过多
- 句式太整齐
- 喜欢三段式排比
- 抽象词太多，具体动作太少
- 过度总结、过度解释
- 模糊归因、空泛拔高
- 人物说话没有区分度
- 连接词太密

### 润色原则

1. 删掉“看起来像在写作”的句子
2. 保留原意，不瞎改情节
3. 优先用动作、感官、停顿代替抽象结论
4. 允许句长变化，避免整齐划一
5. 让角色说话像角色，不像一个统一模型

如果只是轻润，不重写结构；如果原稿 AI 味很重，可分段重写。

---

## 十三、模式切换判断

### 用户一句话需求 → 模式映射

- “帮我开本新书” → 立项模式
- “帮我补设定” → 设定模式
- “做个大纲” → 规划模式
- “写第 5 章” → 章节模式
- “看看最近节奏” → 连载模式
- “这章有没有 bug” → 审校模式
- “把这段改得自然点” → 润色模式
- “帮我做写作学习计划 / 我现在最该学什么” → 学习模式
- “帮我拆《三体》风格 / 做成风格卡 / 存进风格库 / 生成风格提示词” → 风格库模式

如果一句话同时包含多个目标，按以下优先级处理：

**立项/设定 > 规划 > 章节 > 审校 > 润色 > 学习 > 风格库**

---

## 十四、输出约束

- **不要擅自推进到下一章**，除非用户明确要求
- **不要偷改核心设定**，涉及根设变更必须先说明影响
- **不要把项目管理内容写进正文**
- **不要把元叙述写进小说正文**（如“读者看到这里会……”）
- **不要为了显得高级而堆抽象词**

---

## 十五、需要按需读取的参考文件

按任务需要，再读取以下文件：

- `references/genre-profiles.md`：不同题材的节奏与钩子配置
- `references/strand-weave.md`：三线节奏与债务规则
- `references/context-contract.md`：章节创作合同模板
- `references/cool-points.md`：爽点设计
- `references/state-tracking-template.md`：状态追踪模板
- `references/project-init-template.md`：项目初始化模板
- `references/chapter-review-template.md`：章节审核报告模板
- `references/chapter-summary-template.md`：章节元数据 / summary 模板
- `references/humanize-checklist.md`：去 AI 味检查清单
- `references/writing-study-plan.md`：写作学习计划与训练模式参考
- `references/style-library-index.md`：风格库索引
- `references/style-library-santi.md`：三体风格参考卡
- `references/style-library-santi-dialogue.md`：三体对白风格专项卡
- `references/character-three-table-template.md`：角色三表模板
- `references/chapter-progression-checklist.md`：章节推进检查表模板
- `references/motivation-change-template.md`：角色动机变化表模板

不要一上来全读；按需读取最相关的那一份。
