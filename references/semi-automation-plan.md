# Semi-Automation Plan

> 目标：把 `novel-studio` 从“文档 + 模板 +流程规则”推进到“半自动可执行工作流”。

## 一、为什么先做半自动，而不是全自动
小说创作仍然高度依赖判断。
所以更现实的路线是：
- 先自动建骨架
- 先自动建 packet / checklist 占位文件
- 先自动生成索引 / 状态文件骨架
- 把“判断”留给人和 agent

## 二、第一批脚本

### 1. `scripts/init_novel_project.py`
作用：
- 初始化 packet-first 项目骨架
- 建立 `.novel-studio/` 内核结构
- 生成 state / meta 基础文件

### 2. `scripts/chapter_startup.py`
作用：
- 为新章节生成 packet 占位文件
- 生成启动清单
- 为后续 chapter-first workflow 准备落点

## 三、后续可扩展脚本
- `writeback_sync.py`：辅助生成回写清单
- `name_lint.py`：检查命名规范
- `link_check.py`：检查 README / card / change log 链接
- `index_refresh.py`：刷新 active indexes

## 四、实施原则
- 先做 scaffold，不抢创作判断权
- 先保证稳定目录落点
- 再逐步增加自动填充能力
