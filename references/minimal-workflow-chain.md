# Minimal Workflow Chain

> 目标：把现有的 scaffold 脚本和规则串成一条最小可运行工作流，让 `novel-studio` 不只是“有很多脚手架”，而是能形成稳定的章节生产链。

---

## 一、最小串联顺序

### 0. 项目初始化（只做一次）
使用：
- `scripts/init_novel_project.py`

结果：
- 建好项目骨架
- 建好 `.novel-studio/`
- 建好 state / meta 基础文件

### 1. 章节启动
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> startup`

结果：
- 生成 chapter packet scaffold
- 生成 chapter startup checklist scaffold

### 2. 章节创作准备（推荐）
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> chapter-full <project-name>`

结果：
- 确保 summary 已存在
- 确保 chapter packet 已存在
- 确保项目母风格卡已存在
- 确保 style overlay 已存在
- 确保 indexes 已存在

### 3. 风格接入（独立使用时）
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> style-full <project-name>`

结果：
- 若无项目母风格卡，则自动生成
- 若无 style overlay，则自动生成
- 生成 style check

### 4. 正文创作
依据：
- chapter packet
- 上一章 summary
- active indexes
- 相关对象卡
- 项目母风格 + 单章风格偏移

### 5. 章节回写
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> writeback`

结果：
- 生成回写检查结果

### 6. 索引刷新
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> refresh`

结果：
- 刷新 / 准备下一章启动所需的 active indexes

---

## 二、可用模式

- `startup`
- `style`
- `style-full`
- `chapter-full`
- `writeback`
- `refresh`
- `full`

### `chapter-full` 当前作用
- 作为章节级创作启动入口
- 在真正写正文前，把 packet / summary / style overlay / indexes 补齐到最低可运行状态

### `full` 当前具备的最小自愈逻辑
- 如果没有项目风格卡，会自动调用 `extract_project_style.py`
- 如果没有 chapter packet，会自动先跑 startup
- 如果没有 summary，会自动补 summary scaffold
- 如果已有项目风格卡但没有 style overlay，会自动调用 `build_style_packet.py`
- 如果没有 state / meta，会自动补 json scaffold
- 如果没有 indexes，会提示并在 refresh 时准备

---

## 三、最小闭环

一章的最小闭环应是：

1. startup
2. chapter-full
3. draft chapter
4. writeback
5. refresh
6. next chapter startup

一句话：

> **新章不是从正文开始，而是从 startup + chapter-full 开始；一章也不是写完正文就结束，而是要走完 writeback + refresh。**
