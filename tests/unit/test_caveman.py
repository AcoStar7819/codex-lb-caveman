from __future__ import annotations

import asyncio
import json
import shutil
import sys
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.core.clock import RealScheduler
from app.core.openai.requests import ResponsesRequest
from app.core.types import JsonValue
from app.modules.api_keys.service import ApiKeyData
from app.modules.proxy import caveman

pytestmark = pytest.mark.unit


def key(enabled: bool) -> ApiKeyData:
    return ApiKeyData(
        id="key",
        name="test",
        key_prefix="sk-test",
        allowed_models=None,
        enforced_model=None,
        enforced_reasoning_effort=None,
        enforced_service_tier=None,
        expires_at=None,
        is_active=True,
        created_at=datetime(2026, 1, 1),
        last_used_at=None,
        caveman_enabled=enabled,
    )


def table() -> str:
    return json.dumps([{"record_id": i, "record_status": "active", "department": "engineering"} for i in range(20)])


@pytest.mark.parametrize("enabled", [False, True])
async def test_policy_preserves_history_and_tool_arguments(monkeypatch, enabled):
    original = table()
    items = [
        {"type": "function_call", "call_id": "a", "name": "read", "arguments": original},
        {"type": "function_call_output", "call_id": "a", "output": original},
    ]
    payload = ResponsesRequest(model="gpt-5.1", instructions="Answer in Russian", input=items)
    engine = AsyncMock(side_effect=[b"small", original.encode()])
    monkeypatch.setattr(caveman, "_engine", engine)
    await caveman.apply_caveman(payload, key(enabled))
    await caveman.apply_caveman(payload, key(enabled))
    assert items[1]["output"] == original
    projected = payload.model_dump()["input"]
    assert projected[0]["arguments"] == original
    assert payload.instructions.startswith("Answer in Russian")
    assert payload.instructions.count(caveman.GUIDANCE) == int(enabled)
    assert projected[1]["output"] == ("[TOON data]\nsmall" if enabled else original)
    assert engine.await_count == (2 if enabled else 0)


@pytest.mark.parametrize("failure", [OSError(), ValueError(), TimeoutError()])
async def test_engine_failure_preserves_original(monkeypatch, failure):
    items = [{"role": "tool", "content": table(), "tool_call_id": "a"}]
    monkeypatch.setattr(caveman, "_engine", AsyncMock(side_effect=failure))
    payload: dict[str, JsonValue] = {"messages": [*items]}
    await caveman.apply_caveman_chat(payload, key(True))
    messages = payload["messages"]
    assert isinstance(messages, list)
    assert messages[1:] == items
    assert items[0]["content"] == table()


async def test_wrong_round_trip_is_rejected(monkeypatch):
    monkeypatch.setattr(caveman, "_engine", AsyncMock(side_effect=[b"small", b"[]"]))
    assert await caveman._compress(table()) == table()


@pytest.mark.parametrize(
    "text",
    [
        '[{"id":1,"id":2},{"id":3}]' * 30,
        json.dumps([{"nested": {"secret": "x" * 600}}] * 2),
        json.dumps([{"large": 2**60, "text": "x" * 600}] * 2),
        json.dumps([{"float": float("nan"), "text": "x" * 600}] * 2),
    ],
)
async def test_unsupported_context_never_starts_engine(monkeypatch, text):
    engine = AsyncMock()
    monkeypatch.setattr(caveman, "_engine", engine)
    assert await caveman._compress(text) == text
    engine.assert_not_called()


@pytest.mark.parametrize("cancel", [True, False])
async def test_cancellation_and_deadline_reap_native_child(monkeypatch, cancel):
    spawn = asyncio.create_subprocess_exec
    started = asyncio.Event()
    children = []

    async def sleeping_child(*args, **kwargs):
        child = await spawn(sys.executable, "-c", "import time; time.sleep(60)", **kwargs)
        children.append(child)
        started.set()
        return child

    monkeypatch.setattr(caveman.asyncio, "create_subprocess_exec", sleeping_child)

    class ShortDeadline(RealScheduler):
        @staticmethod
        def fail_after(delay, shield=False, reason=None):
            return RealScheduler.fail_after(0.2, shield=shield, reason=reason)

    items: list[JsonValue] = [{"type": "function_call_output", "call_id": "a", "output": table()}]
    task = asyncio.create_task(caveman._project(items, scheduler=ShortDeadline()))
    await started.wait()
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        assert await task == items
    assert children[0].returncode is not None


@pytest.mark.skipif(shutil.which("caveman-engine") is None, reason="Caveman Engine is bundled in Docker")
async def test_real_engine_round_trip():
    original = table()
    result = await caveman._compress(original)
    assert result.startswith("[TOON data]\n")
    assert len(result) < len(original)
    restored = await caveman._engine("decode", result.removeprefix("[TOON data]\n").encode())
    assert json.loads(restored) == json.loads(original)
