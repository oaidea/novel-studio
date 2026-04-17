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

### 2. 风格接入
使用：
- `scripts/extract_project_style.py`（项目级）
- `scripts/build_style_packet.py`（章节级）

结果：
- 项目母风格卡 scaffold
- 单章风格调用 scaffold

### 3. 正文创作
依据：
- chapter packet
- 上一章 summary
- active indexes
- 相关对象卡
- 项目母风格 + 单章风格偏移

### 4. 章节回写
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> writeback`

结果：
- 生成回写检查结果

### 5. 索引刷新
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> refresh`

结果：
- 刷新 / 准备下一章启动所需的 active indexes

### 6. 风格检查
使用：
- `scripts/workflow_runner.py <project-dir> <chapter-id> style`

结果：
- 生成风格一致性检查 scaffold

---

## 二、可用模式

- `startup`
- `style`
- `writeback`
- `refresh`
- `full`

### `full` 当前具备的最小判断逻辑
- 如果没有项目风格卡，会提示先生成母风格
- 如果没有 chapter packet，会自动先跑 startup
- 如果没有 indexes，会提示并在 refresh 时准备
- 如果没有 summaries，会提示 packet-first 连续性仍偏弱

---

## 三、最小闭环

一章的最小闭环应是：

1. startup
2. packet
3. style overlay
4. draft chapter
5. writeback
6. refresh
7. style check
8. next chapter startup

一句话：

> **新章不是从正文开始，而是从 startup 开始；一章也不是写完正文就结束，而是要走完 writeback + refresh + style check。**
