# 章节元数据 / Summary 模板

用于每章写完后的项目内更新，适合写入 `.novel-studio/summaries/ch_XXXX.md` 或整理成结构化记录。

```md
# ch_XXXX 摘要

## 本章核心事件
- 
- 
- 

## 章节功能
- 主线推进：
- 人物关系推进：
- 世界观/设定推进：

## 出场角色状态变化
- 角色名：原状态 → 新状态
- 角色名：原状态 → 新状态

## 重要信息揭示
- 
- 

## 新增伏笔
- [ID] 内容：

## 推进/回收的旧伏笔
- [ID] 处理结果：推进 / 部分回收 / 完全回收

## 关键物品 / 资源变化
- 获得：
- 失去：
- 消耗：

## 本章情绪节拍
- 开头：
- 中段：
- 结尾：

## 章末钩子
- 类型：危机钩 / 信息钩 / 情绪钩 / 渴望钩 / 反转钩
- 内容：
- 强度：强 / 中 / 弱

## 下一章承接点
- 
- 
```

## 如果要写成结构化 YAML，可用：

```yaml
chapter: ch_XXXX
summary:
  core_events:
    - 
    - 
  function:
    quest: 
    fire: 
    constellation: 
  reveals:
    - 
  new_foreshadowing:
    - id: 
      content: 
  resolved_foreshadowing:
    - id: 
      status: advance
  character_state_changes:
    - name: 
      from: 
      to: 
  inventory_changes:
    gained: []
    lost: []
    used: []
  ending_hook:
    type: 
    content: 
    strength: 
  next_chapter_setup:
    - 
```
