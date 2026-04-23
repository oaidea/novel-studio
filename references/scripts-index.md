# Scripts Index

当前脚本：
- `scripts/init_novel_project.py`：初始化 layered / packet-first 项目骨架
- `scripts/chapter_startup.py`：为新章节生成 packet 与启动清单骨架
- `scripts/extract_project_style.py`：为项目生成母风格卡 scaffold
- `scripts/build_style_packet.py`：为单章生成风格调用说明 scaffold
- `scripts/build_object_state_summary.py`：为单章生成对象状态摘要 scaffold
- `scripts/build_input_pack.py`：为单章生成模型极简版 / 模型标准版 / 人工审阅版输入包
- `scripts/writeback_sync.py`：为章节回写生成 checklist scaffold
- `scripts/index_refresh.py`：初始化 / 刷新活动索引 scaffold
- `scripts/style_check.py`：为单章生成风格一致性检查 scaffold
- `scripts/governance_audit.py`：审计 layered 项目是否存在治理漂移（目录缺失、state/meta 漏项、入口引用失效等）
- `scripts/workflow_runner.py`：串行触发最小 workflow chain
- `scripts/smoke_regression.py`：创建临时 fixture，跑 init / doctor / startup / chapter-full 的最小回归链路

当前状态：
- 已提供第一版 scaffold / 轻量实用工具混合层
- 已具备最小 smoke regression，帮助防止脚手架、doctor、chapter-full 主链路再次漂移
- 后续可继续扩展 naming lint / link check / true style extraction / true index refresh / full workflow runner / deeper governance doctor
