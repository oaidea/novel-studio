# Workflow Demo

> 最小示例：如何用现有脚手架跑一轮章节工作流。

## Step 1：初始化项目（只做一次）
```bash
scripts/init_novel_project.py <project-dir>
```

## Step 2：启动某章
```bash
scripts/workflow_runner.py <project-dir> ch_0007 startup
```

## Step 3：补齐章节创作条件
```bash
scripts/workflow_runner.py <project-dir> ch_0007 chapter-full <project-name>
```

## Step 4：正文写作（人工 / agent）
依赖：
- packet
- summary
- indexes
- 对象卡
- style overlay

## Step 5：回写与刷新
```bash
scripts/workflow_runner.py <project-dir> ch_0007 writeback
scripts/workflow_runner.py <project-dir> ch_0007 refresh
```

## Step 6：一键跑全链（当前版）
```bash
scripts/workflow_runner.py <project-dir> ch_0007 full <project-name>
```
