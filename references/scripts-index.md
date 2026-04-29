# Scripts Index

当前脚本：
- `scripts/init_novel_project.py`：初始化 layered / packet-first 项目骨架
- `scripts/chapter_startup.py`：为新章节生成 packet 与启动清单骨架
- `scripts/extract_project_style.py`：为项目生成母风格卡 scaffold
- `scripts/build_style_packet.py`：为单章生成风格调用说明 scaffold
- `scripts/build_object_state_summary.py`：为单章生成对象状态摘要 scaffold
- `scripts/build_input_pack.py`：为单章生成模型极简版 / 模型标准版 / 人工审阅版输入包
- `scripts/writeback_sync.py`：为章节回写生成 checklist scaffold
- `scripts/index_refresh.py`：初始化 / 刷新活动索引 scaffold（含 clips）
- `scripts/style_check.py`：为单章生成风格一致性检查 scaffold
- `scripts/camera_follow_check.py`：轻量检查镜头跟随叙述风险（抽象气氛词、上帝视角抢跑、感知锚点不足、疑似 POV 发散）
- `scripts/observer_description_check.py`：轻量检查第三方描述风险（作者硬夸、群体尬吹、信息越权、缺少具体反应）
- `scripts/scene_tension_check.py`：轻量检查场景张力风险（阻力/代价不足、对白空转、纯气氛静态段）
- `scripts/information_release_check.py`：轻量检查信息释放风险（解释腔、真相/机制词过密、已知信息对白）
- `scripts/direct_api_writer.py`：从 input pack 组装隔离请求并可选调用 OpenAI-compatible Chat Completions API；默认 dry-run，输出到 `.novel-studio/outputs/`
- `scripts/ns_model_config.py`：管理 Novel Studio 全局直连 API 模型配置与工作模式切换（list / global set / global show / workmode set / workmode show）
- `scripts/ns_api_log.py`：查看和管理直连 API 调用日志（支持摘要、筛选、JSON 导出）
- `scripts/governance_audit.py`：审计 layered 项目是否存在治理漂移（目录缺失、state/meta 漏项、入口引用失效等）
- `scripts/consistency_audit.py`：审计 state / chapter-meta / chapter files / packet-first 产物是否互相一致
- `scripts/naming_lint.py`：审计文件命名是否出现状态塞进文件名、final-v2 漂移、对象区非 kebab-case 等命名坏味道
- `scripts/workflow_runner.py`：串行触发最小 workflow chain
- `scripts/ns_session.py`：项目级会话历史与状态保护，支持断点恢复（start/complete/fail/status/clear/global-last）
- `scripts/clip_manager.py`：创建 / 列表 / 查看 / 更新 / 状态流转 / merge Clip 的最小管理脚本
- `scripts/chapter_overview.py`：生成单章 overview，汇总 chapter files + clips + packet-first 产物
- `scripts/clip_overview.py`：生成项目级 Clip 总览（当前支持 `unassigned / all`）
- `scripts/clip_stats_sync.py`：把 Clip 统计回写进 `state.json` 与 `chapter-meta.json`
- `scripts/retire_asset.py`：把 chapter / clip 移入 `chapters/retired/`，默认退出创作流
- `workflow_runner.py ... chapter-full` 当前会自动触发 chapter overview + clip stats sync

当前状态：
- 已提供第一版 scaffold / 轻量实用工具混合层
- 已具备最小 smoke regression，帮助防止脚手架、doctor、chapter-full 主链路再次漂移
- `workflow_runner.py ... doctor` 当前会同时跑 governance audit + consistency audit + naming lint
- 后续可继续扩展 link check / true style extraction / true index refresh / full workflow runner / deeper governance doctor
