# Gemini 4 Only Enforcement Policy

The `gemini4-only-guard` plugin is active globally and blocks non-Gemini-4 worker/subagent calls via `PreToolUse` hooks:

1. **Swarm (`swarm`)**: Every `add` or `model` call MUST explicitly pass a Gemini 4 model (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-medium`, or `gemini-4-hydrogen-low`). Never omit `model` (which defaults to `gemini-flash-worker-agy`), and never pick `gemini-3.8-*`, `claude-*`, `gpt-oss-*`, or `gemini-pro-orchestrator-*`.
2. **Subagents (`invoke_subagent`)**: Never pass `Model: "flash"` or `Model: "flash_lite"` (including for `browser`). Use `inherit` (or `pro`) only; if an unavailable tier is requested, the hook denies the call immediately.
