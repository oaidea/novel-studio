# Chapter 片段 / Clip 管理：MVP 开发任务单

> 用途：把“Chapter 管理中新增片段 / Clip”从需求讨论转成可执行的开发任务清单，作为 Novel Studio 的实现底稿。
>
> 范围：仅覆盖 **MVP 第一版** 必做能力；增强体验项放到后续版本处理。

---

## 一、目标

让 Novel Studio 在 chapter 管理体系中正式支持 **片段 / Clip**，做到：

- 能创建
- 能读取
- 能修改
- 能查询
- 能纳入 chapter 资产盘点

一句话：

> **Clip 要从“普通 markdown 文件”升级为“可对话管理的章节局部资产对象”。**

---

## 二、MVP 边界

### 2.1 本版必须支持

- 识别 `chapters/clips/`
- 识别 `type: clip`
- 读写 Clip frontmatter
- 创建 / 编辑 Clip
- 管理 Clip 状态与状态流转
- 自动维护 `updated_at`
- 按 `chapter / status / updated_at` 查询 Clip
- 在 chapter overview / chapter 盘点中纳入 clips

### 2.2 本版暂不强求

- Clip 与 Draft 的引用关系图
- Clip 演化链可视化
- 多章节归属
- 从正文自动拆 Clip
- 高级 UI 或复杂可视化面板
- 对 `merged_into` 做严格强校验

---

## 三、Clip 对象定义（MVP 基线）

### 3.1 对象名称

- 中文：**片段**
- 英文：**Clip**

两者为同义概念。

### 3.2 对象定位

Clip 是**章节相关的局部内容资产**，不是整章稿件。

### 3.3 与 Draft / Revision 的边界

- **Clip**：局部资产，可复用、可悬空、可后续并入正文
- **Draft**：整章推进单位
- **Revision**：章节版本改写链的一部分

一句话判定规则：

> **Revision 是版本改写，Clip 是局部资产。**

### 3.4 最小元数据模板

```md
---
type: clip
title: 母亲记忆闪回
chapter: unassigned
status: active
created_at: 2026-04-23 16:49:00 +08:00
updated_at: 2026-04-23 16:49:00 +08:00
tags: []
merged_into:
---

正文内容……
```

### 3.5 字段规则

- `type`：固定为 `clip`
- `title`：可中文
- `chapter`：只允许单值；未归属时固定为 `unassigned`
- `status`：`active | merged | archived | discarded`
- `created_at`：创建时间，创建后不改
- `updated_at`：最后修改时间，所有写操作都要刷新
- `tags`：数组，MVP 允许为空
- `merged_into`：可空；当状态为 `merged` 时建议填写

### 3.6 正文规则

- 正文允许为空或仅有简短占位内容
- Clip 的合法性以元数据为主要判定依据

---

## 四、开发任务单

下表按“任务名 / 说明 / 优先级 / 依赖 / 验收标准”组织。

---

### T1. 定义 Clip 内部对象模型

**优先级**：P0  
**依赖**：无

**说明**

在系统内部新增 Clip 的统一数据结构，不再把它仅视为普通 markdown 文件。

建议字段：

- `type`
- `title`
- `chapter`
- `status`
- `created_at`
- `updated_at`
- `tags`
- `merged_into`
- `content`
- `path`
- `slug`（若实现侧需要）

**验收标准**

- 系统内部存在明确的 Clip 数据结构
- 该结构可以由文件解析得到
- 该结构可以稳定写回文件

---

### T2. 识别 `chapters/clips/` 目录

**优先级**：P0  
**依赖**：T1

**说明**

更新项目扫描逻辑，让 `chapters/clips/` 成为 chapter 管理体系中的合法目录。

**验收标准**

- 项目扫描时不会忽略 `chapters/clips/`
- 目录中的 markdown 文件能进入项目资源范围
- 没有 clips 的老项目仍保持兼容

---

### T3. 实现 Clip frontmatter 解析与写回

**优先级**：P0  
**依赖**：T1, T2

**说明**

读取并写回以下字段：

- `type`
- `title`
- `chapter`
- `status`
- `created_at`
- `updated_at`
- `tags`
- `merged_into`

关键规则：

- `chapter: unassigned` 必须合法
- `tags` 默认空数组
- `merged_into` 可空
- 正文允许为空

**验收标准**

- 合法 clip 文件可被正确读取
- 修改后可稳定写回，不破坏 frontmatter 结构
- 写回后正文与字段位置保持可读

---

### T4. 实现 Clip 创建能力

**优先级**：P0  
**依赖**：T3

**说明**

支持创建一个新的 Clip 文件，并自动写入最小模板。

默认行为：

- 存放到 `chapters/clips/`
- 自动生成文件名 slug
- `type: clip`
- `chapter: unassigned`
- `status: active`
- `tags: []`
- `created_at = updated_at = now`
- `merged_into:` 空

输入至少支持：

- `title`
- 可选 `chapter`
- 可选 `tags`
- 可选正文

**验收标准**

- 能成功创建一个合法 clip 文件
- frontmatter、文件路径、正文都正确
- 默认值符合规则

---

### T5. 实现 Clip 编辑能力

**优先级**：P0  
**依赖**：T3

**说明**

支持修改：

- 正文
- `title`
- `chapter`
- `status`
- `tags`
- `merged_into`

统一要求：

- 任何写操作都刷新 `updated_at`
- `created_at` 不变

**验收标准**

- 改任意受支持字段都能正确落盘
- `updated_at` 自动变化
- `created_at` 保持不变

---

### T6. 实现文件名 slug 生成与冲突处理

**优先级**：P1  
**依赖**：T4

**说明**

创建 Clip 时，从标题或内容生成英文 slug 文件名；若重名则自动追加后缀。

建议形式：

- `mother-memory-flash.md`
- `mother-memory-flash-2.md`

规则：

- 文件名尽量稳定
- `title` 与文件名解耦
- 标题可改，文件名不强制同步改

**验收标准**

- 连续创建重名片段不会覆盖旧文件
- 文件名可读、稳定、可预测

---

### T7. 实现 Clip 状态枚举与合法值校验

**优先级**：P0  
**依赖**：T3

**说明**

将状态值限制为：

- `active`
- `merged`
- `archived`
- `discarded`

**验收标准**

- 非法状态不会被静默写入
- 非法值至少会报错、拒绝或触发明确提示

---

### T8. 实现状态流转规则

**优先级**：P0  
**依赖**：T7, T5

**说明**

实现以下合法流转：

- `active -> merged / archived / discarded`
- `merged -> active / archived`
- `archived -> active / discarded`
- `discarded -> active`

原则：

- 跨语义大跳转尽量先回 `active`
- 非法流转应被拒绝

**验收标准**

- 系统中存在统一的状态变更入口或校验逻辑
- 非法流转不会落盘
- 合法流转符合设计文档

---

### T9. 实现 merge 专用操作

**优先级**：P1  
**依赖**：T8

**说明**

将“标记为 merged”从普通 status 修改中抽成显式操作语义。

merge 至少应做：

- `status = merged`
- 可写入 `merged_into`
- 刷新 `updated_at`

建议：

- 若未提供 `merged_into`，允许执行，但给出提示

**验收标准**

- 系统存在明确的 merge 操作
- merge 后对象状态正确
- `merged_into` 可被顺带写入

---

### T10. 将 Clip 纳入项目索引

**优先级**：P0  
**依赖**：T2, T3

**说明**

让 Clip 进入项目可查询索引，而不是每次都通过临时扫盘回答。

索引至少应记录：

- `title`
- `path`
- `chapter`
- `status`
- `updated_at`
- `tags`

**验收标准**

- 系统层能快速列出所有 clips
- 不依赖全文扫描也能回答基础查询

---

### T11. 实现 Clip 基础列表能力

**优先级**：P0  
**依赖**：T10

**说明**

支持列出所有 Clip，默认按 `updated_at` 倒序返回。

建议列表字段：

- `title`
- 文件名或路径
- `chapter`
- `status`
- `updated_at`
- `tags`

**验收标准**

- “列出所有片段” 能稳定得到结果
- 排序默认是最近修改优先

---

### T12. 实现基础筛选能力

**优先级**：P0  
**依赖**：T10, T11

**说明**

MVP 至少支持按以下条件筛选：

- `chapter`
- `status`
- 最近修改排序

必须支持回答：

- 某章有哪些 clips
- 哪些是 `unassigned`
- 哪些是 `active`
- 最近修改了哪些 clips

**验收标准**

- 基础筛选逻辑可复用
- 结果符合 chapter / status / updated_at 预期

---

### T13. 将 Clip 纳入章节资产盘点

**优先级**：P0  
**依赖**：T10, T12

**说明**

升级 chapter 管理逻辑：

对于某章，除了查看：

- published
- drafts
- candidates
- revisions

还应能查看：

- clips

根据 `chapter` 字段把 Clip 归入对应章节；`chapter: unassigned` 的 Clip 应单独归类。

**验收标准**

- 盘点某章时可看到关联 clips
- 未归属片段可独立查看
- clips 不再混进 drafts/revisions

---

### T14. 为 chapter overview 增加 Clips 分区

**优先级**：P1  
**依赖**：T13

**说明**

即便第一版只是文本输出，chapter overview 也应有显式结构：

- Published
- Drafts
- Candidates
- Revisions
- Clips

**验收标准**

- 用户问“第 4 章现在有什么”时，输出中有独立 Clips 分区
- Clips 作为章节资产被清晰呈现

---

### T15. 接入对话查询意图映射

**优先级**：P1  
**依赖**：T11, T12, T13

**说明**

让常见自然语言查询可以稳定映射到底层 Clip 查询能力。

MVP 至少覆盖：

- “列出所有片段”
- “列出第 4 章片段”
- “看未归属片段”
- “看最近修改的片段”
- “看 active 的 clips”

**验收标准**

- 对话层可稳定调用底层查询
- 支持“片段”与“clip”两种说法

---

### T16. 接入对话更新意图映射

**优先级**：P1  
**依赖**：T4, T5, T8, T9

**说明**

让常见自然语言更新操作映射到底层 create / edit / status / merge 能力。

MVP 至少覆盖：

- “创建一个片段”
- “把这段存成片段”
- “把这个片段归到 ch_004”
- “把这个片段标为 merged”
- “把这个片段恢复 active”

**验收标准**

- 对话层可稳定调用底层更新逻辑
- 常见操作不需要用户手写 frontmatter

---

### T17. 统一 `updated_at` 自动维护

**优先级**：P0  
**依赖**：T5, T8, T9

**说明**

为所有写操作建立统一入口或统一更新时间逻辑，避免漏更或误更。

规则：

- 任何内容、元数据、标识信息变更都必须更新 `updated_at`
- 纯读取类操作不得修改 `updated_at`

**验收标准**

- 不存在“改了内容但时间没变”
- 不存在“只是查看却更新时间变了”

---

### T18. 确保旧项目兼容

**优先级**：P0  
**依赖**：T2, T3, T10, T13

**说明**

Clip 支持属于新增能力，不能破坏现有 chapter 管理逻辑。

需保证：

- 已有 `published / drafts / candidates / revisions` 工作流保持兼容
- 没有 clips 的项目也正常工作
- 老项目不会因为新增 clips 支持而报错

**验收标准**

- 旧结构项目能正常加载
- 无 clips 项目不受影响
- 新旧逻辑可并存

---

### T19. 补边界样例测试

**优先级**：P1  
**依赖**：T3, T4, T5, T8, T10

**说明**

至少准备以下样例：

1. 正常 clip
2. `chapter: unassigned`
3. 空正文 clip
4. `merged` 但无 `merged_into`
5. 非法状态
6. 重名标题创建
7. 合法 / 非法状态流转

**验收标准**

- 合法样例能通过
- 非法样例能被明确拒绝或报错
- 行为与规则一致

---

## 五、建议开发顺序

### Phase 1：打底

1. T1 定义 Clip 对象模型
2. T2 识别 `chapters/clips/`
3. T3 frontmatter 解析与写回

### Phase 2：让对象活起来

4. T4 创建 Clip
5. T5 编辑 Clip
6. T6 slug 生成与冲突处理

### Phase 3：加规则

7. T7 状态枚举与校验
8. T8 状态流转
9. T9 merge 专用操作

### Phase 4：让它可管理

10. T10 项目索引
11. T11 基础列表
12. T12 基础筛选

### Phase 5：接入 chapter 与对话

13. T13 章节资产盘点
14. T14 chapter overview 的 Clips 分区
15. T15 / T16 对话意图映射

### Phase 6：补护栏

16. T17 `updated_at` 统一维护
17. T18 旧项目兼容检查
18. T19 边界样例测试

---

## 六、最小落地包（建议首批实现）

如果需要进一步压缩首批开发范围，优先实现以下 8 项：

- T1 对象模型
- T2 目录识别
- T3 frontmatter 解析写回
- T4 创建
- T5 编辑
- T8 状态流转
- T10 索引
- T13 章节资产盘点

这 8 项完成后，Clip 就已经从概念进入可用状态。

---

## 七、后续版本建议

### Next（体验增强）

- 按 `tags` 查询
- 更强的 `merged_into` 约束
- 按 `title` 和 `slug` 双通道定位片段
- unassigned clips 独立视图
- 更智能的 slug 生成
- 空正文片段提示

### Later（后续扩展）

- Clip 与 Draft 的引用关系
- Clip 演化链
- 可视化资产视图
- 多章节归属
- 从正文自动拆 Clip
- 更复杂的智能判断

---

## 八、一句话结论

> **MVP 的关键，不是“多一个文件夹”，而是让 Clip 作为 chapter 局部资产拥有对象身份、状态规则、查询能力，以及与 chapter 盘点的稳定集成。**
