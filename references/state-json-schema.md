# State JSON Schema (v2 Draft)

> 用途：统一 `.novel-studio/state.json` 的推荐字段，使其既能支持 packet-first 工作流，也能承载长期连载项目的项目级状态。
>
> 这不是强校验格式，而是**推荐结构**。最小可用字段可以更少，但建议随着项目进入长期维护逐步补齐。

## 推荐字段

```json
{
  "project": "项目名",
  "volume": "当前卷 / 当前阶段名",
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
  "current_phase": "当前整体写作阶段说明",
  "main_strand": {
    "quest": "主任务线 / 剧情主线",
    "fire": "关系线 / 情感线 / 人物张力线",
    "constellation": "母设定线 / 长线真相线"
  },
  "active_conflicts": [
    "当前主冲突1",
    "当前主冲突2"
  ],
  "key_open_threads": [
    "当前未收口的重要线索1",
    "当前未收口的重要线索2"
  ],
  "strand_balance": {
    "quest_last推进": "ch_000X",
    "fire_last推进": "ch_000X",
    "constellation_last推进": "ch_000X"
  }
}
```

---

## 字段说明

### 顶层字段
- `project`：项目名
- `volume`：当前卷名、阶段名，或当前正在处理的分部
- `version`：状态文件本身的维护版本，可选
- `last_updated`：最后更新时间，建议 `YYYY-MM-DD`
- `status`：项目状态，例如 `active / paused / archived`
- `writing_mode`：当前默认写作模式，例如 `packet-first`

### `summary`
项目级数量摘要，用于快速判断当前正文状态。

推荐包括：
- `total_chapters_planned`
- `chapters_published`
- `chapters_candidate`
- `chapters_draft`
- `chapters_reference_only`

### `current_phase`
一句话描述当前写作阶段。

例子：
- `前三章已发布；ch_004 为待发布稿件；ch_005/006 为正常写作稿件`
- `第一卷中段重构中，暂停继续后写`

### `main_strand`
用于定义项目的主线分层，便于后续做节奏平衡与承接检查。

默认建议三类：
- `quest`：剧情推进主线
- `fire`：关系 / 情绪 / 人物张力线
- `constellation`：长线真相 / 母设定线

如果项目不用这三个名字，也可以替换成自己的命名体系。

### `active_conflicts`
当前正在推进的主要冲突列表。

### `key_open_threads`
当前仍未收口、但必须持续跟踪的重要线索或谜团。

### `strand_balance`
记录三条主线最近一次被明确推进到哪一章，用于防止某条线长期失踪。

---

## 最小可运行版本

如果项目还很早期，至少建议保留：

```json
{
  "project": "项目名",
  "volume": "",
  "last_updated": "YYYY-MM-DD",
  "status": "active",
  "writing_mode": "packet-first",
  "current_phase": "",
  "active_conflicts": [],
  "key_open_threads": []
}
```

---

## 使用建议

推荐在以下时机更新 `state.json`：
1. 发布新章后
2. 当前主写章节变化后
3. 主冲突或当前阶段发生变化后
4. 长线未收口问题发生增删后

一句话原则：
> `state.json` 不负责存细节全文，而负责存项目当前最值得被快速看见的状态。 
