# Chapter Meta Schema (v2 Draft)

> 用途：统一 `.novel-studio/chapter-meta.json` 的章节级元数据结构。
>
> 目标不是把正文细节都塞进这里，而是让项目能快速回答：
> - 每章当前是什么状态
> - 这一章讲了什么
> - 这一章推进了什么
> - 这一章是否已具备 packet / summary / 回写状态

## 推荐结构

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
      "key_events": [
        "关键事件1",
        "关键事件2"
      ],
      "hasPacket": false,
      "hasSummary": false,
      "cardsUpdated": false,
      "timeAnchor": "该章时间锚点",
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

## 字段说明

### 基础字段
- `id`：章节 ID，推荐格式 `ch_001`
- `title`：章节标题
- `status`：章节状态，推荐值：`published / candidate / draft / archived / reference`
- `phase`：更细的工作流阶段说明，例如 `定稿 / 候选 / 试写 / 重构中`
- `word_count`：字数，可空
- `published_date`：发布日期，可空

### 摘要字段
- `summary`：该章的一两句话结构化摘要
- `key_events`：该章关键事件列表

### 工作流字段
- `hasPacket`：是否已生成 chapter packet
- `hasSummary`：是否已生成 chapter summary
- `cardsUpdated`：相关对象卡 / 变化记录是否已回写
- `timeAnchor`：该章时间锚点

### 主线平衡字段
- `strand.quest`：剧情主线推进强度
- `strand.fire`：关系 / 情感 / 张力线推进强度
- `strand.constellation`：长线真相 / 母设定线推进强度

这里的数值可以按项目自定义。
常见做法：
- `0`：基本未推进
- `1`：有推进
- `2`：明显推进

---

## 最小可运行版本

如果项目还在初期，至少建议保留：

```json
{
  "chapters": [
    {
      "id": "ch_001",
      "title": "章节标题",
      "status": "draft",
      "summary": "",
      "hasPacket": false,
      "hasSummary": false,
      "cardsUpdated": false,
      "timeAnchor": ""
    }
  ]
}
```

---

## 使用建议

推荐在以下时机更新 `chapter-meta.json`：
1. 新建章节时补 entry
2. 章节状态流转时（draft → candidate → published）
3. 生成 packet / summary 后
4. 回写对象卡后
5. 发布后补 `published_date`、`summary` 与 `key_events`

一句话原则：
> `chapter-meta.json` 是章节索引与状态面板，不是正文替代品。 
