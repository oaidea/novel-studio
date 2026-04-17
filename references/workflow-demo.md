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

## Step 3：正文写作（人工 / agent）
依赖：
- packet
- summary
- indexes
- 对象卡
- style overlay

## Step 4：回写与检查
```bash
scripts/workflow_runner.py <project-dir> ch_0007 writeback
scripts/workflow_runner.py <project-dir> ch_0007 refresh
scripts/workflow_runner.py <project-dir> ch_0007 style
```

## Step 5：一键跑最小链（当前版）
```bash
scripts/workflow_runner.py <project-dir> ch_0007 full <project-name>
```

### `full` 模式当前会自动补的内容
- 项目风格卡 scaffold（通过 `extract_project_style.py`）
- summary scaffold
- state.json scaffold
- chapter-meta.json scaffold
- chapter packet scaffold（通过 startup）
- style overlay scaffold（通过 `build_style_packet.py`）
