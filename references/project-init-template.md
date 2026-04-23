# 项目初始化模板（Layered / Packet-First）

> 当前模板以 `fanchenlu` 实战项目验证过的分层结构为基准。
> 目标不是把所有信息塞进少数总文件，而是从一开始就把：**入口层、设定层、正文流、发散流、结构化工作内核** 分开。

将 `<项目名>` 替换成真实名称后使用。

## 建议创建的目录骨架

```text
<项目名>/
├── README.md
├── analysis/
│   └── README.md
├── brainstorm/
│   └── README.md
├── chapters/
│   ├── README.md
│   ├── published/
│   ├── candidates/
│   ├── early-drafts/
│   ├── drafts/
│   └── revisions/
├── docs/
│   ├── README.md
│   └── project-notes.md
├── nav/
│   ├── README.md
│   ├── characters.md
│   ├── outline.md
│   ├── timeline.md
│   ├── foreshadowing.md
│   └── state_tracking.md
├── settings/
│   ├── README.md
│   ├── core/
│   ├── world/
│   └── subsettings/
│       ├── README.md
│       ├── project-style-card.md
│       ├── characters/
│       │   ├── README.md
│       │   ├── changes/
│       │   └── templates/
│       ├── relationships/
│       │   └── README.md
│       ├── timeline/
│       │   ├── README.md
│       │   └── templates/
│       ├── foreshadowing/
│       │   ├── README.md
│       │   ├── cards/
│       │   └── templates/
│       ├── spaces/
│       │   ├── README.md
│       │   ├── cards/
│       │   ├── changes/
│       │   └── templates/
│       ├── scenes/
│       │   ├── README.md
│       │   ├── cards/
│       │   ├── changes/
│       │   └── templates/
│       ├── events/
│       │   ├── README.md
│       │   └── templates/
│       └── items/
│           ├── README.md
│           ├── cards/
│           ├── changes/
│           └── templates/
├── workflow/
│   ├── README.md
│   ├── chapter-progress.md
│   └── outline-next-chapters.md
└── .novel-studio/
    ├── README.md
    ├── state.json
    ├── chapter-meta.json
    ├── summaries/
    ├── packets/
    ├── indexes/
    │   ├── active-characters.md
    │   ├── active-events.md
    │   ├── active-spaces.md
    │   ├── active-scenes.md
    │   └── pending-foreshadowing.md
    └── logs/
```

---

## 入口层分工

### `README.md`
回答：
- 这个仓库是什么
- 顶层目录怎么分工
- 第一次进来先看哪里

### `docs/project-notes.md`
回答：
- 当前项目写到哪
- 当前最优先任务是什么
- 如果要继续写 / 修设定 / 回看正文，该先点开什么

### `nav/`
回答：
- 人物摘要
- 分卷 / 长线摘要
- 时间线摘要
- 伏笔摘要
- 项目状态跳转

**一句话原则：**
> README 管结构，project-notes 管工作入口，nav 管快速摘要。

---

## 各层职责

### 1. `chapters/` —— 正文创作流
只放进入正文流的文件：
- 已发布版
- 候选稿
- 早期草稿
- 修订稿

推荐状态目录：
- `published/`
- `candidates/`
- `early-drafts/`
- `drafts/`
- `revisions/`

### 2. `brainstorm/` —— 发散流
放：
- 结构试探
- 线索讨论
- 标题试探
- 暂不进入正文流的实验稿

### 3. `settings/` —— 设定主区
- `core/`：总设定 / 上位真相 / 长线母文件
- `world/`：世界规则 / 边界 / 不可写穿层
- `subsettings/`：人物、关系、时间、伏笔、空间、场景、事件、物件等对象层资料

### 4. `workflow/` —— 推进管理层
放：
- 章节进度
- 近章规划
- 协作流程
- 当前写作优先级

### 5. `.novel-studio/` —— 结构化工作内核
放：
- `state.json`
- `chapter-meta.json`
- chapter summaries
- chapter packets
- active indexes
- workflow logs

---

## 推荐最小可运行集

如果用户暂时不想把所有对象层都建满，至少保证：

```text
README.md
docs/project-notes.md
chapters/
brainstorm/
nav/
settings/core/
settings/world/
settings/subsettings/characters/
settings/subsettings/timeline/
settings/subsettings/foreshadowing/
workflow/
.novel-studio/state.json
.novel-studio/chapter-meta.json
```

---

## 推荐 starter 文件内容

### `README.md`

```md
# <项目名>

这是一个长期维护的小说项目仓库。

## 顶层分工
- `chapters/`：正文创作流
- `brainstorm/`：发散流
- `settings/`：设定主区
- `workflow/`：推进管理
- `nav/`：快速摘要入口
- `.novel-studio/`：结构化工作内核

## 推荐查看顺序
1. `README.md`
2. `docs/project-notes.md`
3. `nav/`
```

### `docs/project-notes.md`

```md
# 项目工作入口

## 当前状态
- 当前正文状态：
- 当前最优先任务：
- 当前母设定收束方向：

## 从这里往哪走
### 要继续写正文
1. `workflow/chapter-progress.md`
2. `chapters/`
3. 必要时回查 `settings/`

### 要修设定
1. `settings/core/`
2. `settings/world/`
3. `settings/subsettings/`
4. `workflow/`

### 要快速回忆摘要
1. `nav/outline.md`
2. `nav/characters.md`
3. `nav/timeline.md`
4. `nav/foreshadowing.md`
```

### `workflow/chapter-progress.md`

```md
# 章节进度记录

## 当前章节状态
- ch_001：

## 当前最优先任务
- 

## 联动维护规则
1. 更新正文或草稿
2. 更新伏笔 / 时间 / 对象层资料
3. 更新本文件
4. 如涉及长线调整，再回写 `settings/core/` / `settings/world/`
```

### `settings/subsettings/project-style-card.md`

```md
# 项目风格卡

## 风格总纲
- 

## 叙事要求
- 

## 对话要求
- 

## 节奏要求
- 

## 禁止倾向
- 
```

---

## `.novel-studio/state.json`（推荐字段）

```json
{
  "project": "<项目名>",
  "volume": "",
  "version": "0.1.0",
  "last_updated": "YYYY-MM-DD",
  "status": "active",
  "writing_mode": "packet-first",
  "summary": {
    "total_chapters_planned": 0,
    "chapters_published": 0,
    "chapters_candidate": 0,
    "chapters_draft": 0,
    "chapters_reference_only": 0
  },
  "current_phase": "",
  "main_strand": {
    "quest": "",
    "fire": "",
    "constellation": ""
  },
  "active_conflicts": [],
  "key_open_threads": [],
  "strand_balance": {
    "quest_last推进": "",
    "fire_last推进": "",
    "constellation_last推进": ""
  }
}
```

### `.novel-studio/chapter-meta.json`（推荐字段）

```json
{
  "chapters": [
    {
      "id": "ch_001",
      "title": "章节标题",
      "status": "published",
      "phase": "定稿 / 候选 / 试写",
      "word_count": null,
      "published_date": null,
      "summary": "一两句话概括该章",
      "key_events": [],
      "hasPacket": false,
      "hasSummary": false,
      "cardsUpdated": false,
      "timeAnchor": "",
      "strand": {
        "quest": 0,
        "fire": 0,
        "constellation": 0
      }
    }
  ]
}
```

---

## 一句话原则

> 初始化模板要服务于长期连载治理；不要把项目做成“少数总文件越写越重”，而要从第一天就让正文流、设定层、导航层、工作流层、结构化内核分工清楚。
