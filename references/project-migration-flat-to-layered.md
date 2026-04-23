# Flat → Layered 项目迁移指南

> 用途：把旧式“少数总文件集中管理”的小说项目，迁移到 Novel Studio 当前的 layered / packet-first 结构。
>
> 适用场景：
> - 旧项目里有大量 `00-项目总览.md / 01-故事主线.md / 03-角色档案.md` 这类总文件
> - 已经能写，但资料越写越重、越找越难
> - 想切换到 `README + project-notes + nav + settings + .novel-studio` 这套长期维护结构

---

## 一、迁移目标

迁移后的目标不是“把旧文件简单挪个目录”，而是把项目拆成五层：

1. **入口层**：`README.md` / `docs/project-notes.md` / `nav/`
2. **正文流**：`chapters/`
3. **发散流**：`brainstorm/`
4. **设定层**：`settings/core` / `settings/world` / `settings/subsettings`
5. **结构化工作内核**：`.novel-studio/`

---

## 二、迁移原则

### 1. 先建骨架，再迁内容
不要边想边乱搬。
先初始化目标结构，再决定每一类旧文件落到哪里。

### 2. 先拆“入口”，再拆“内容”
很多旧项目最大的问题不是内容少，而是所有内容都挤在少数总文件里。
先解决入口层级，后面迁移会顺很多。

### 3. 总文件不一定删除，但不能继续当唯一真相
旧总文件可以先保留，作为过渡参考。
但迁移完成后，正式依据要切换到：
- `settings/`
- `workflow/`
- `.novel-studio/`

### 4. 优先迁移最常用、最影响续写稳定性的内容
优先级通常是：
1. 章节正文
2. 当前主设定
3. 人物资料
4. 时间线
5. 伏笔
6. 关系 / 空间 / 场景
7. 事件 / 物件

---

## 三、旧文件 → 新结构映射建议

### 常见旧结构

```text
<project>/
├── 00-项目总览.md
├── 01-故事主线.md
├── 02-世界观设定.md
├── 03-角色档案.md
├── 04-力量体系.md
├── 05-写作风格.md
├── 06-分卷大纲.md
├── 07-章节大纲.md
├── 08-时间线.md
├── 09-势力与地图.md
├── 10-伏笔与回收.md
├── 11-状态追踪.md
├── 12-当前进度.md
└── 正文章节/
```

### 推荐映射

| 旧文件 | 新落点 | 说明 |
|---|---|---|
| `00-项目总览.md` | `README.md` + `docs/project-notes.md` | 结构说明进 README，当前工作状态进 project-notes |
| `01-故事主线.md` | `settings/core/` | 主线、立意、总推进方向属于上位设定 |
| `02-世界观设定.md` | `settings/world/` | 世界规则、边界、禁忌优先放 world |
| `03-角色档案.md` | `settings/subsettings/characters/` | 拆成人物卡；不再长期维护单个总表 |
| `04-力量体系.md` | `settings/world/` | 力量规则、层级、代价属于 world |
| `05-写作风格.md` | `settings/subsettings/project-style-card.md` | 迁成项目风格卡 |
| `06-分卷大纲.md` | `settings/core/` 或 `workflow/` | 稳定分卷结构放 core，当前近章推进放 workflow |
| `07-章节大纲.md` | `workflow/` | 当前近章规划与章节设计不宜继续塞在总文件 |
| `08-时间线.md` | `settings/subsettings/timeline/` | 拆成时间锚点文件 |
| `09-势力与地图.md` | `settings/core/` / `settings/world/` / `settings/subsettings/spaces/` | 视内容拆分 |
| `10-伏笔与回收.md` | `settings/subsettings/foreshadowing/` | 迁成伏笔管理表 / 伏笔卡 |
| `11-状态追踪.md` | `.novel-studio/state.json` + `.novel-studio/chapter-meta.json` + `nav/state_tracking.md` | 总状态拆成结构化文件 |
| `12-当前进度.md` | `docs/project-notes.md` + `workflow/chapter-progress.md` | 当前优先任务与章节进度分开 |
| `正文章节/` | `chapters/` | 再细分 `published / candidates / early-drafts / drafts / revisions` |

---

## 四、推荐迁移顺序

### Step 1：初始化新骨架
建议先运行：

```bash
scripts/init_novel_project.py <project-dir>
```

如果项目已存在，则手动补齐缺目录与缺文件也可以。

### Step 2：迁移正文
先把正文类文件分流到：
- `chapters/published/`
- `chapters/candidates/`
- `chapters/early-drafts/`
- `chapters/drafts/`
- `chapters/revisions/`

### Step 3：建立入口层
补齐：
- `README.md`
- `docs/project-notes.md`
- `nav/`

### Step 4：迁移上位设定
把旧总文件里真正属于母设定 / 世界边界的部分拆到：
- `settings/core/`
- `settings/world/`

### Step 5：迁移对象层
逐类拆出：
- `characters/`
- `timeline/`
- `foreshadowing/`
- `relationships/`
- `spaces/`
- `scenes/`
- `events/`
- `items/`

### Step 6：补 `.novel-studio/` 内核
至少补：
- `state.json`
- `chapter-meta.json`
- `summaries/`
- `packets/`
- `indexes/`

### Step 7：跑治理审计
建议运行：

```bash
scripts/governance_audit.py <project-dir>
```

看是否仍有：
- 缺目录
- 缺入口文件
- `chapter-meta.json` 漏章
- 文档引用失效

---

## 五、迁移中的常见判断题

### 1. 这段内容该进 `core` 还是 `world`？
- 决定总真相 / 上位因果 / 长线结构 → `core`
- 决定规则 / 边界 / 不可写穿层 → `world`

### 2. 角色资料是保留总表还是拆卡？
优先拆卡。
总表可以保留为过渡索引，但不要继续让它承担全部维护职责。

### 3. 章节大纲放哪？
- 长期稳定的卷级结构：`settings/core/`
- 当前推进中的近章规划：`workflow/`

### 4. 旧文件删不删？
迁移初期建议：
- 先保留
- 标记 legacy / archive
- 等新结构跑稳再决定是否归档或删除

---

## 六、迁移完成的最低标准

迁移完成后，至少应能做到：
- 新人进项目先看 `README.md` 知道结构
- 继续写时先看 `docs/project-notes.md`
- 快速回忆时看 `nav/`
- 正文文件都在 `chapters/`
- 设定主依据都在 `settings/`
- 当前状态能在 `.novel-studio/state.json` 和 `chapter-meta.json` 里快速看见

---

## 七、一句话原则

> 迁移的目标不是“把旧文件搬散”，而是把项目从“少数总文件硬扛一切”升级成“分层结构可持续维护”。
