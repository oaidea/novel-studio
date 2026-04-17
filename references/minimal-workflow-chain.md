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
- 生成“本章可写状态报告”
- 报告中包含缺失项与下一步建议动作

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
