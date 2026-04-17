# Style Automation Plan

> 目标：把项目级母风格与章节风格调用，从“文档规则”推进到“半自动脚手架”。

## 第一批脚本

### 1. `scripts/extract_project_style.py`
作用：
- 为项目生成母风格卡 scaffold
- 为后续外部样本复刻 / 项目内章节提纯预留落点

### 2. `scripts/build_style_packet.py`
作用：
- 为单章生成风格调用说明 scaffold
- 把 chapter packet 与项目母风格卡接起来

## 后续可继续扩展
- 从已写章节抽取高频风格特征
- 对多个样本章节做风格交集提纯
- 写后进行 style consistency 检查
