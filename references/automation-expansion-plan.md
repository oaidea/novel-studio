# Automation Expansion Plan

> 当前已从“文档 + 模板”推进到“半自动脚手架”。下一批脚本重点是闭环与刷新。

## 新增脚本

### 1. `scripts/writeback_sync.py`
作用：
- 为写完一章后的回写动作生成 checklist scaffold
- 把 packet-first 的闭环落地到日志层

### 2. `scripts/index_refresh.py`
作用：
- 初始化 / 刷新 `.novel-studio/indexes/`
- 为下一章低 token 启动提供稳定入口

### 3. `scripts/style_check.py`
作用：
- 为某章生成风格一致性检查 scaffold
- 把“项目母风格 → 单章校验”接成闭环

## 当前阶段判断
这三者补上后，`novel-studio` 将从“半自动化骨架”进一步进入“可闭环的半自动工作流雏形”。
