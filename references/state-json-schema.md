# State JSON Schema (Draft)

> 用途：统一 `.novel-studio/state.json` 的基本字段，方便后续 packet-first 工作流稳定使用。

```json
{
  "project": "项目名",
  "currentArc": "当前卷或当前阶段",
  "currentChapter": "ch_000X",
  "currentTimeAnchor": "当前时间锚点",
  "currentConflicts": [
    "当前主冲突1",
    "当前主冲突2"
  ],
  "topPriorities": [
    "当前最优先待办1",
    "当前最优先待办2"
  ],
  "pendingForeshadowing": [
    "未回收伏笔1",
    "未回收伏笔2"
  ]
}
```
