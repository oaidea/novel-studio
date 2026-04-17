# Project Governance for Novel Studio

> 基于《凡尘箓》项目整理经验抽象出的通用项目治理规则。

## 一、适用场景
当小说项目出现以下问题时，启用本规则：
- 文件越堆越乱
- 设定混在正文、脑暴稿、导航稿里
- 人物 / 场景 / 空间的信息找不到
- 章节推进后，对象变化无记录
- README、工作说明、导航摘要互相打架
- 文件名开始出现“最终版-再改版-v2”式失控

## 二、核心治理原则

### 1. 创作流与发散流分离
- `chapters/`：实际创作文本
- `brainstorm/`：结构试探、线索讨论、发散稿

### 2. 总设定与子设定分层
- `settings/core/`：总设定 / 总纲 / 上位真相
- `settings/world/`：规则层 / 长线边界
- `settings/subsettings/`：人物、关系、时间线、伏笔、空间、场景等子设定

### 3. 对象卡与变化记录分离
对以下对象统一采用：
- 卡片本体：当前稳定状态
- 变化记录：变化过程、章节原因、后续影响

对象范围：
- 人物
- 空间
- 场景

### 4. 入口层级统一
- `README.md`：总入口
- `docs/project-notes.md`：工作入口
- `nav/`：快速摘要入口

### 5. 导航不代替母设定
`nav/` 只做摘要；若与 `settings/` 冲突，以 `settings/` 为准。

### 6. 状态写在目录，不写在文件名
- 正文流 → `chapters/`
- 发散稿 → `brainstorm/`
- 卡片 → `cards/`
- 变化记录 → `changes/`

## 三、推荐目录骨架

```text
<project>/
├── README.md
├── docs/
│   └── project-notes.md
├── analysis/
├── chapters/
├── brainstorm/
├── nav/
├── settings/
│   ├── core/
│   ├── world/
│   └── subsettings/
│       ├── characters/
│       ├── relationships/
│       ├── timeline/
│       ├── foreshadowing/
│       ├── spaces/
│       └── scenes/
├── workflow/
└── .novel-studio/
```

## 四、升级输出建议
治理一个项目时，优先输出：
1. 问题诊断
2. 新结构建议
3. 迁移映射清单
4. 命名规范
5. 卡片 / 变化记录 / 模板清单
6. 入口层级说明
