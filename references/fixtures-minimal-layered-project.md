# Fixture: minimal-layered-project

这是 `novel-studio` 的最小回归样板说明，不是正式小说项目，也不是长期维护仓库。

用途：
- 说明当前 layered / packet-first 项目最小应该长什么样
- 给 smoke regression 脚本提供人工对照基准
- 防止脚手架、doctor、chapter-full 的预期结构再次漂移

## 目标

该 fixture 关注的是**结构与工作流链路**，不是内容质量。

它要覆盖的最小能力：
1. `init_novel_project.py` 能生成当前标准骨架
2. `governance_audit.py` / `workflow_runner.py ... doctor` 能通过
3. `chapter_startup.py` 能生成 packet 与 startup checklist
4. `chapter-full` 能产出：
   - summary
   - packet
   - project style card
   - style overlay
   - object state summary
   - input packs
   - readiness report

## 当前最小结构期待

```text
<fixture>/
├── README.md
├── analysis/
├── brainstorm/
├── chapters/
│   ├── published/
│   ├── candidates/
│   ├── early-drafts/
│   ├── drafts/
│   └── revisions/
├── docs/
│   └── project-notes.md
├── nav/
├── settings/
│   ├── core/
│   ├── world/
│   └── subsettings/
│       ├── project-style-card.md
│       ├── characters/
│       ├── relationships/
│       ├── timeline/
│       ├── foreshadowing/
│       ├── spaces/
│       ├── scenes/
│       ├── events/
│       └── items/
├── workflow/
└── .novel-studio/
    ├── state.json
    ├── chapter-meta.json
    ├── summaries/
    ├── packets/
    ├── indexes/
    └── logs/
```

## 推荐回归命令

```bash
python3 scripts/smoke_regression.py
```

如果该脚本通过，说明当前最关键的：
- 项目骨架
- 治理审计
- chapter startup
- chapter-full 最小链路

仍然是通的。
