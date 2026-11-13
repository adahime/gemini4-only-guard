# gemini4-only-guard

[English](#english) | [中文](#中文)

---

## English

An Antigravity plugin that blocks non-Gemini-4 model selection in `swarm` workers and `flash` / `flash_lite` tier downgrades in `invoke_subagent` calls via `PreToolUse` hooks and an active rule file.

### What it does

- **`swarm` (`add` / `model` actions)**
  - Allows only model names or display names starting with `gemini-4-` or `Gemini 4 ` (for example `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-xhigh`).
  - Returns `{"decision": "deny"}` with an error reason if `model` is omitted (which otherwise falls back to `gemini-flash-worker-agy`) or if any other model is passed (such as `gemini-3.8-*`, `claude-*`, `gpt-oss-*`, `gemini-pro-orchestrator-*`).
  - Management actions (`status`, `models`, `kill`, `title`, etc.) are allowed through normally.
- **`invoke_subagent`**
  - Denies `Model: "flash"` and `Model: "flash_lite"` (including `browser` calls if passed as `flash`).
  - Allows `"inherit"` (default) and `"pro"`.
- **Rule file (`rules/AGENTS.md`)**
  - Instructs the coordinator and subagents to use Gemini 4 models only.

### Scope & Limitations

- Blocks tool-level worker spawning and model switching (`swarm`, `invoke_subagent`) at hook time.
- Does not remove models from the Antigravity UI dropdown and does not override the main chat model you select manually in the UI.

### Directory layout

```text
gemini4-only-guard/
├── plugin.json
├── hooks.json
├── rules/
│   └── AGENTS.md
├── scripts/
│   └── gemini4_guard.py
├── tests/
│   └── test_gemini4_guard.py
├── LICENSE
└── README.md
```

### Installation

Clone or copy this folder into your Antigravity global plugins directory:

- **Windows (PowerShell)**:
  ```powershell
  git clone https://github.com/adahime/gemini4-only-guard.git "$env:USERPROFILE\.gemini\config\plugins\gemini4-only-guard"
  ```
- **macOS / Linux**:
  ```bash
  git clone https://github.com/adahime/gemini4-only-guard.git ~/.gemini/config/plugins/gemini4-only-guard
  ```

Requires Python 3 (`python` available on `PATH`). You can verify or toggle the plugin in Antigravity's Customizations / Plugins view.

### Tests

```bash
python tests/test_gemini4_guard.py
```

---

## 中文

一个用于 Antigravity 的插件，通过 `PreToolUse` 钩子与规则文件，在调用 `swarm` 和 `invoke_subagent` 之前拦截非 Gemini 4 模型与 `flash` 降级调用，直接拒绝并报错。

### 功能说明

- **拦截 `swarm`（`add` / `model` 动作）**
  - 仅放行以 `gemini-4-` 或 `Gemini 4 ` 开头的模型（如 `gemini-4-argon-high`、`gemini-4-argon-medium`、`gemini-4-hydrogen-high`、`gemini-4-hydrogen-xhigh`）。
  - 如果未传 `model`（默认会落到 `gemini-flash-worker-agy`），或传入了 `gemini-3.8-*`、`claude-*`、`gpt-oss-*`、`gemini-pro-orchestrator-*` 等其他模型，钩子直接返回 `{"decision": "deny"}` 并输出报错原因，阻止工具执行。
  - `status`、`models`、`kill`、`title` 等管理操作正常放行。
- **拦截 `invoke_subagent`**
  - 拒绝 `Model` 为 `flash` 或 `flash_lite` 的调用（包含 `browser` 子代理）。
  - 仅放行 `inherit`（默认跟随主对话模型）与 `pro`。
- **附带规则（`rules/AGENTS.md`）**
  - 在上下文规则中要求仅使用 Gemini 4 系列模型。

### 使用边界与说明

- 本插件在工具调用阶段硬拦截 `swarm` 与 `invoke_subagent`，防止后台自动切到其他模型。
- 无法隐藏 Antigravity 客户端 UI 下拉菜单里的模型选项，也不会改变你在主聊天窗口中手动选择的主模型。

### 安装方法

将本仓库克隆或复制到 Antigravity 全局插件目录即可（需要系统 `PATH` 中有 `python`）：

- **Windows (PowerShell)**:
  ```powershell
  git clone https://github.com/adahime/gemini4-only-guard.git "$env:USERPROFILE\.gemini\config\plugins\gemini4-only-guard"
  ```
- **macOS / Linux**:
  ```bash
  git clone https://github.com/adahime/gemini4-only-guard.git ~/.gemini/config/plugins/gemini4-only-guard
  ```

安装后可在 Antigravity 的自定义/插件页面查看并开关 `Gemini 4 Only Guard`。

### 运行测试

```bash
python tests/test_gemini4_guard.py
```
