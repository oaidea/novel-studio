# Project Skeleton Template

> 用途：初始化一个长期小说项目时使用的标准目录骨架参考。
>
> 当前权威版本以：
> - `references/project-init-template.md`
> - `scripts/init_novel_project.py`
>
> 为准；本文件提供的是**简版结构概览**，避免在多个文档里复制一整套骨架后再次漂移。

```text
<project>/
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

## 最小可运行集
- `README.md`
- `docs/project-notes.md`
- `chapters/`
- `brainstorm/`
- `nav/`
- `settings/core/`
- `settings/world/`
- `settings/subsettings/characters/`
- `settings/subsettings/timeline/`
- `settings/subsettings/foreshadowing/`
- `workflow/`
- `.novel-studio/state.json`
- `.novel-studio/chapter-meta.json`

## 使用建议
- 如果要初始化真实项目，优先看 `references/project-init-template.md`
- 如果要真正创建骨架，优先运行 `scripts/init_novel_project.py <project-dir>`
- 如果是旧项目迁移，优先看 `references/project-migration-flat-to-layered.md`
