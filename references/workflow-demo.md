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

## Step 3：生成项目风格卡 scaffold
```bash
scripts/extract_project_style.py <project-dir> <project-name>
```

## Step 4：生成章节风格调用 scaffold
```bash
scripts/build_style_packet.py <project-dir> ch_0007 settings/subsettings/project-style-card.md
```

## Step 5：正文写作（人工 / agent）
依赖：
- packet
- summary
- indexes
- 对象卡
- style overlay

## Step 6：回写与检查
```bash
scripts/workflow_runner.py <project-dir> ch_0007 writeback
scripts/workflow_runner.py <project-dir> ch_0007 refresh
scripts/workflow_runner.py <project-dir> ch_0007 style
```

## Step 7：一键跑最小链（当前版）
```bash
scripts/workflow_runner.py <project-dir> ch_0007 full
```

### `full` 模式会做的提醒
- 没有项目风格卡时提示先生成
- 没有 packet 时自动先 startup
- 没有 indexes 时提示 refresh 会补
- 没有 summary 时提示连续性仍偏弱
