# Entrypoint Layering

> 用于统一小说项目的入口层级，避免 README、项目说明、导航摘要互相打架。

## 一、三层入口

### 1. README.md
负责讲：
- 仓库是什么
- 顶层目录怎么分工
- 第一次进来应该看哪里

### 2. docs/project-notes.md
负责讲：
- 当前项目状态
- 当前最优先任务
- 准备开始动手时先看哪些文件

### 3. nav/
负责讲：
- 人物摘要
- 第一部 / 分卷摘要
- 时间线摘要
- 伏笔摘要
- 状态摘要

## 二、分工原则
- README 管结构
- project-notes 管工作入口
- nav 管快速摘要

## 三、冲突原则
如果 nav 与 settings 冲突，以 settings 为准。
如果 project-notes 与 settings 冲突，以 settings + workflow 为准。
