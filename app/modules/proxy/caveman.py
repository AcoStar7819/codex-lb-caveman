"""Opt-in, reversible context projection using the official local Caveman Engine.

The SDK's recovery-based middleware cannot execute recovery tools on our clients.
Only stateless TOON is used here; inference and its streaming remain in codex-lb.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import subprocess
from copy import deepcopy

import anyio

from app.core.clock import REAL_SCHEDULER, Scheduler
from app.core.openai.requests import ResponsesCompactRequest, ResponsesRequest
from app.core.types import JsonValue
from app.modules.api_keys.service import ApiKeyData

logger = logging.getLogger(__name__)

GUIDANCE = (
    "[Caveman: concise output] Use few words while preserving correctness and necessary detail. "
    "Skip filler, repeated summaries and unsolicited explanations. Keep the user's language. "
    "Keep code, commands, identifiers and required output formats exact. "
    "Tool context marked TOON is a lossless table: header names apply to each row."
)
_MAX_BYTES = 256 * 1024
_MAX_SEGMENTS = 8
_SLOTS = asyncio.Semaphore(4)
_TOON_PREFIX = "[TOON data]\n"


def _unique_object(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _table(text: str) -> list[dict[str, JsonValue]] | None:
    if len(text) < 512 or len(text.encode("utf-8")) > _MAX_BYTES:
        return None
    try:
        value = json.loads(text, object_pairs_hook=_unique_object)
    except (ValueError, RecursionError):
        return None
    if not isinstance(value, list) or len(value) < 2 or not isinstance(value[0], dict) or not value[0]:
        return None
    keys = list(value[0])
    for row in value:
        if not isinstance(row, dict) or list(row) != keys:
            return None
        for cell in row.values():
            if isinstance(cell, (dict, list)):
                return None
            if isinstance(cell, float) and not math.isfinite(cell):
                return None
            # Avoid a native JSON decoder's floating-point precision boundary.
            if isinstance(cell, (int, float)) and abs(cell) > 2**53 - 1:
                return None
    return value


async def _engine(action: str, data: bytes) -> bytes:
    process = await asyncio.create_subprocess_exec(
        "caveman-engine",
        "toon",
        action,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    try:
        output, _ = await process.communicate(data)
        if process.returncode:
            raise ValueError("engine failed")
        return output
    finally:
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            with anyio.CancelScope(shield=True):
                await process.wait()


async def _compress(text: str) -> str:
    original = _table(text)
    if original is None:
        return text
    async with _SLOTS:
        encoded = await _engine("encode", text.encode("utf-8"))
        candidate = _TOON_PREFIX + encoded.decode("utf-8")
        if len(candidate.encode("utf-8")) >= len(text.encode("utf-8")):
            return text
        decoded = json.loads(await _engine("decode", encoded), object_pairs_hook=_unique_object)
        # JSON serialization distinguishes booleans, strings, numbers and nulls.
        if json.dumps(decoded, sort_keys=True, ensure_ascii=False) != json.dumps(
            original, sort_keys=True, ensure_ascii=False
        ):
            return text
        return candidate


async def _project(items: JsonValue, *, chat: bool = False, scheduler: Scheduler = REAL_SCHEDULER) -> JsonValue:
    if not isinstance(items, list):
        return items
    projected = deepcopy(items)
    remaining = _MAX_SEGMENTS
    try:
        with scheduler.fail_after(2):
            for item in projected:
                if not isinstance(item, dict):
                    continue
                if chat:
                    if item.get("role") != "tool":
                        continue
                    field = "content"
                else:
                    if item.get("type") not in {"function_call_output", "custom_tool_call_output"}:
                        continue
                    field = "output"
                content = item.get(field)
                if isinstance(content, str):
                    if _table(content) is not None:
                        if remaining == 0:
                            break
                        remaining -= 1
                        item[field] = await _compress(content)
                elif isinstance(content, list):
                    for part in content:
                        if not isinstance(part, dict) or part.get("type") not in {"input_text", "text"}:
                            continue
                        text = part.get("text")
                        if isinstance(text, str) and _table(text) is not None and remaining:
                            remaining -= 1
                            part["text"] = await _compress(text)
    except (OSError, ValueError, TimeoutError, RecursionError):
        # Never log the engine stderr or customer content; keep the whole original
        # projection on failure, rather than a partially transformed history.
        logger.warning("caveman_projection_unavailable")
        return items
    return projected


async def apply_caveman(
    payload: ResponsesRequest | ResponsesCompactRequest,
    api_key: ApiKeyData | None,
    *,
    scheduler: Scheduler = REAL_SCHEDULER,
) -> None:
    if api_key is None or not api_key.caveman_enabled:
        return
    if GUIDANCE not in payload.instructions:
        payload.instructions = f"{payload.instructions}\n\n{GUIDANCE}".strip()
    payload.input = await _project(payload.input, scheduler=scheduler)


async def apply_caveman_chat(payload: dict[str, JsonValue], api_key: ApiKeyData | None) -> None:
    if api_key is None or not api_key.caveman_enabled:
        return
    messages = await _project(payload.get("messages"), chat=True)
    if not isinstance(messages, list):
        return
    if not any(isinstance(item, dict) and item.get("content") == GUIDANCE for item in messages):
        messages = [{"role": "system", "content": GUIDANCE}, *messages]
    payload["messages"] = messages
