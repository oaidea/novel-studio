# Direct API Writing / 直连 API 写作通道

> 用途：让 Novel Studio 在写作时使用独立的 OpenAI-compatible Chat Completions / Anthropic Messages API 通道，由 NS 自己读取 input pack、组装请求、保存输出，避免当前聊天系统上下文污染写作资料。

---

## 定位

Direct API Writing 是 Novel Studio 的**隔离写作执行层**。

- **配置/调试指令永远走 OpenClaw 系统对话模型**
- **创作/写作/修稿类任务受全局工作模式管辖**：
  - `system`（系统模型模式）→ 走 OpenClaw 系统对话模型
  - `direct`（直连模式）→ 走 direct API，不允许直接借用当前聊天系统模型完成正文、审校、润色或风格判断

```text
NS 项目文件 → input pack → direct_api_writer.py → 指定模型 API → 输出到项目文件
```

它不是替代 packet-first，而是 packet-first 的执行器。

允许在未配置模型时运行的只有确定性文件工具，例如项目初始化、chapter-full/input-pack 生成、doctor、smoke、naming lint、consistency audit。它们不能生成正文判断，只能产出脚手架、索引、报告和文件状态。

---

## 适合场景

- 正式章节初稿生成
- 章节改写 / 重写
- 去AI味旁路稿
- 风格一致性改稿
- 希望写作上下文只来自项目文件，不混入当前聊天上下文
- 需要指定模型、base_url、temperature 等参数

---

## 安全原则

1. **默认 dry-run**：默认只生成请求预览，不真实调用 API。
2. **密钥只走环境变量**：不把 API key 写进项目文件或日志。
3. **输出旁路保存**：默认写入 `.novel-studio/outputs/`，不覆盖正文。
4. **上下文可审计**：每次请求保存 manifest，记录实际带入哪些文件。
5. **不自动发送真实请求**：真实 API 调用必须由操作者明确指定 `--execute`。

---

## 当前 direct writer 支持协议

只支持两类核心协议：

- `openai-completions` → `POST <baseUrl>/chat/completions`
- `anthropic-messages` → `POST <baseUrl>/messages`

其他协议（如 `openai-codex-responses` / `openai-responses` 等）明确不支持，validate 或执行时会要求重新选择模型。

---

## 配置方式

### 工作模式

Novel Studio 有两个全局工作模式，影响创作任务的行为：

```bash
# 查看当前模式
python3 scripts/ns_model_config.py workmode show

# 系统模型模式：所有任务走 OpenClaw 系统对话
python3 scripts/ns_model_config.py workmode set system

# 直连模式：创作/写作/修稿走 direct API（默认）
python3 scripts/ns_model_config.py workmode set direct
```

**规则：**
- 配置和调试指令（模型配置、查看 log、doctor 等）**永远走系统模型**
- 创作/写作/修稿受 workMode 控制：`system` → 系统模型，`direct` → 直连 API
- `direct_api_writer.py --execute` 在系统模型模式下会直接拒绝执行

### 从 OpenClaw 系统模型配置选择

先列出当前系统模型：

```bash
python3 scripts/ns_model_config.py list
```

配置全局直连 API 模型（**不再需要项目级配置，全局一份即可**）：

```bash
python3 scripts/ns_model_config.py global set
```

也可以用 alias / full id / 序号非交互选择：

```bash
python3 scripts/ns_model_config.py global set --select LSJ --non-interactive
python3 scripts/ns_model_config.py global set --select lsj/gpt-5.5 --non-interactive
python3 scripts/ns_model_config.py global set --select 1 --non-interactive
```

选中后会**自动验证模型连通性**（发送最小 API 请求）。验证失败则放弃导入，不保存配置。
跳过验证：`--skip-validate`。

它会写入 `.novel-studio/global-config.json` 的 `directApi` 字段：

```json
{
  "workMode": "direct",
  "directApi": {
    "systemModel": "lsj/gpt-5.5",
    "model": "gpt-5.5",
    "api": "openai-completions",
    "baseUrl": "https://codex.ooooo.codes/v1",
    "apiKey": "sk-...",
    "apiKeyEnv": "NOVEL_STUDIO_API_KEY_LSJ",
    "temperature": 0.7,
    "maxTokens": 131072,
    "modelConfig": { ... },
    "providerConfig": { ... }
  }
}
```

注意：该文件会保存已验证可用的模型配置快照，**包括 apiKey**。命令行展示和 manifest 会对 apiKey 脱敏。

查看当前全局配置：

```bash
python3 scripts/ns_model_config.py global show
```

### 手动环境变量

推荐使用环境变量：

```bash
export NOVEL_STUDIO_API_KEY='...'
export NOVEL_STUDIO_BASE_URL='https://api.example.com/v1'
export NOVEL_STUDIO_MODEL='model-name'
```

也可命令行覆盖；命令行参数优先于 `.novel-studio/global-config.json` 的 `directApi` 配置：

```bash
python3 scripts/direct_api_writer.py <project-dir> ch_005 \
  --base-url https://api.example.com/v1 \
  --model model-name \
  --api-key-env NOVEL_STUDIO_API_KEY
```

---

## 输入来源

默认读取：

```text
.novel-studio/logs/<chapter>-input-pack.md
```

该文件中的路径会被展开为实际内容。

默认只接受项目内相对路径，防止误读项目外文件。

---

## 输出位置

默认输出：

```text
.novel-studio/outputs/<chapter>-direct-api-<timestamp>.md
.novel-studio/outputs/<chapter>-direct-api-<timestamp>.manifest.json
```

manifest 记录：

- project root
- chapter id
- model
- base_url host/path（不含 key）
- input pack
- included files
- prompt profile
- output file
- dry-run / execute 状态

---

## 推荐命令

### 1. 先生成 chapter-full

```bash
python3 scripts/workflow_runner.py <project-dir> ch_005 chapter-full
```

### 2. dry-run 预览请求

如果尚未配置全局直连模型，先运行：

```bash
python3 scripts/ns_model_config.py global set
```

没有 `.novel-studio/global-config.json` 的 `directApi` 配置且未显式传入 `--model` + `--base-url` 时，direct writer 会直接退出并提示配置模型。

```bash
python3 scripts/direct_api_writer.py <project-dir> ch_005 --dry-run
```

### 3. 查看和重配模型

查看当前全局直连 API 配置：

```bash
python3 scripts/ns_model_config.py global show
```

如需更换直连模型，重新运行：

```bash
python3 scripts/ns_model_config.py global set
```

### 4. 明确执行真实请求

```bash
python3 scripts/direct_api_writer.py <project-dir> ch_005 --execute
```

---

## 提示词结构

Direct API 默认使用两层消息：

1. system：Novel Studio 写作规则、隔离上下文规则、禁止发明项目外信息
2. user：章节任务、展开后的 input pack 内容、输出要求

默认要求模型只输出正文或改稿结果，不输出分析过程。

---

## 红线

- 不把系统聊天历史带入 API 请求。
- 不把 API key 写入 manifest。
- 不默认覆盖 `chapters/published` 或 `chapters/drafts`。
- 不在未审阅 input pack 前盲目执行。
- 不把“项目外私有文件”通过路径塞入 input pack。
