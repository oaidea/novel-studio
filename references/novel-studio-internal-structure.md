# `.novel-studio` Internal Structure

> 用途：定义 packet-first 写作下 `.novel-studio/` 的内部目录职责，让 chapter packet、chapter summary、state、indexes 有稳定落点。

---

## 一、目标

`.novel-studio/` 不应该只是零散 json 存放处，而应成为：

> **小说项目的结构化工作内核**

当项目进入长期维护、低 token 创作、packet-first 工作流后，这里负责承载：
- 章节 packet
- 章节摘要
- 状态文件
- 索引文件
- 元数据

---

## 二、推荐结构

```text
.novel-studio/
├── state.json                  # 项目全局状态
├── chapter-meta.json           # 章节级元数据
├── summaries/                  # 每章结构化摘要
│   └── ch_XXXX-summary.md
├── packets/                    # 每章 chapter packet
│   └── ch_XXXX-packet.md
├── indexes/                    # 结构化索引
│   ├── active-characters.md
│   ├── active-events.md
│   ├── active-spaces.md
│   ├── active-scenes.md
│   └── pending-foreshadowing.md
└── logs/                       # 可选：工作流日志 / 自动生成日志
```

---

## 三、各目录职责

### 1. `state.json`
记录项目全局状态，例如：
- 当前写到第几章
- 当前卷 / 阶段
- 当前主要冲突
- 当前最优先待办
- 当前时间锚点

### 2. `chapter-meta.json`
记录章节级元数据，例如：
- 每章标题
- 章节状态（published / draft / candidate）
- 是否已有 packet
- 是否已有 summary
- 是否已回写卡片

### 3. `summaries/`
每章一个结构化摘要。

用途：
- 给下一章提供最小承接上下文
- 避免回读上一章全文

### 4. `packets/`
每章一个 chapter packet。

用途：
- 压缩该章写作所需上下文
- 让正文默认依赖 packet 而不是前文全文

### 5. `indexes/`
用于放“当前活动对象索引”。

例如：
- 当前在场人物
- 当前未收口事件
- 当前正在使用的空间 / 场景
- 当前未回收伏笔

这些索引的价值在于：
- 新章节启动时，先快速知道“现在有哪些东西是活的”
- 而不是靠全文搜索推断

### 6. `logs/`
可选。

未来如果有自动化脚本，可以把：
- 初始化日志
- 命名检查日志
- 链接检查日志

放在这里。

---

## 四、推荐读取顺序

在 packet-first 工作流下，创作新章节时推荐按以下顺序读取：

1. `.novel-studio/packets/ch_XXXX-packet.md`
2. `.novel-studio/summaries/ch_XXXX-summary.md`
3. `.novel-studio/indexes/active-characters.md`
4. `.novel-studio/indexes/active-events.md`
5. `.novel-studio/indexes/active-spaces.md`
6. `.novel-studio/indexes/active-scenes.md`
7. `.novel-studio/indexes/pending-foreshadowing.md`
8. 再按需去 `settings/` 读取对象卡

---

## 五、推荐更新顺序

每写完一章后：

1. 更新 `summaries/`
2. 更新 `chapter-meta.json`
3. 更新 `state.json`
4. 更新 `indexes/`
5. 回写对象卡与变化记录

---

## 六、一句话原则

> **`.novel-studio/` 是正文之外的结构化工作内核；它的职责不是存全文，而是存低 token 创作真正需要的最小结构化上下文。**
