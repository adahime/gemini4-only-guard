#!/usr/bin/env python3
"""PreToolUse guard enforcing Gemini 4 models only for swarm and subagent calls."""

from __future__ import annotations

import json
import sys


def _emit(payload: dict) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()
    return 0


def _allow() -> int:
    return _emit({"decision": "allow"})


def _deny(reason: str) -> int:
    return _emit({"decision": "deny", "reason": reason})


def _is_gemini4_model(name: str) -> bool:
    norm = name.strip().lower()
    if not norm:
        return False
    return norm.startswith("gemini-4-") or norm.startswith("gemini 4 ")


def main() -> int:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace").strip()
    if not raw:
        return _deny("GEMINI4_ONLY_GUARD_ERROR: Empty PreToolUse hook payload.")

    try:
        payload = json.loads(raw)
    except Exception as exc:
        return _deny(f"GEMINI4_ONLY_GUARD_ERROR: Invalid PreToolUse JSON payload: {exc}")

    tool_call = payload.get("toolCall") if isinstance(payload, dict) else None
    if not isinstance(tool_call, dict):
        return _allow()

    tool_name = str(tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    if not isinstance(args, dict):
        args = {}

    if tool_name == "swarm":
        action = str(args.get("action") or "").strip().lower()
        if action in ("add", "model"):
            model = str(args.get("model") or "").strip()
            if not model:
                return _deny(
                    "GEMINI4_ONLY_GUARD_ERROR: swarm action requires explicit model='gemini-4-*' "
                    "(omitting model falls back to gemini-flash-worker-agy, which is blocked)."
                )
            if not _is_gemini4_model(model):
                return _deny(
                    f"GEMINI4_ONLY_GUARD_ERROR: Non-Gemini-4 model {model!r} is blocked. "
                    "Only gemini-4-* models (e.g. gemini-4-argon-high/medium/low, "
                    "gemini-4-hydrogen-high/xhigh/medium/low) are allowed."
                )
        return _allow()

    if tool_name == "invoke_subagent":
        raw_tier = args.get("Model") if args.get("Model") is not None else args.get("model")
        tier = str(raw_tier if raw_tier is not None else "inherit").strip().lower()
        if tier in ("flash", "flash_lite", "flash-lite"):
            return _deny(
                f"GEMINI4_ONLY_GUARD_ERROR: invoke_subagent Model={tier!r} is blocked. "
                "Only 'inherit' or 'pro' (or explicit gemini-4-*) is allowed."
            )
        if tier in ("inherit", "pro") or _is_gemini4_model(tier):
            return _allow()
        return _deny(
            f"GEMINI4_ONLY_GUARD_ERROR: Unrecognized/non-Gemini-4 subagent model tier {tier!r} blocked."
        )

    return _allow()


if __name__ == "__main__":
    raise SystemExit(main())
