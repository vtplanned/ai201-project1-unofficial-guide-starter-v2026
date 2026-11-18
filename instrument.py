#!/usr/bin/env python3
"""
Structured request logging — the unit 9 extension.

`serve.py` shipped with "deliberately no logging, no timing and no metrics in
this file." This is the layer that adds them, kept in its own module so the
route handlers stay readable and so the thing being tested is a thing with a
name.

Every request appends one JSON object to `logs/requests.jsonl` — one record per
line, so it can be read back with `grep`, `jq`, or four lines of Python,
without a parser that understands log sentences.

Fields on every record:

    ts              UTC timestamp, millisecond resolution
    request_id      12 hex chars, so one request can be followed across lines
    route           "/ask" or "/health"
    method          HTTP verb
    outcome         answered | refused | bad_request | error
    status          the HTTP status actually returned
    duration_ms     wall clock for the whole request, measured here

Plus, on /ask:

    question        what came in, verbatim
    answer_chars    size of what went out
    best_distance   the retrieval distance the gate judged
    refused         whether the gate stopped it
    sources         the files the answer cited
    model_calls     API calls this request made (0 for a refusal)
    prompt_tokens   tokens in
    output_tokens   tokens out
    error           "TypeName: message", only when something broke

A failed request writes a record too. A failure that shows up only as an
absence is one you can never find afterwards.
"""

import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(os.getenv("AI201_LOG_DIR", "logs"))
LOG_FILE = LOG_DIR / "requests.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def new_request_id() -> str:
    return uuid.uuid4().hex[:12]


def write(record: dict) -> None:
    """Append one record. Logging must never be the thing that breaks a request."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        pass


@contextmanager
def observe(route: str, method: str, **fields):
    """Time a request, capture its token cost, and write one record at the end.

    Yields a dict the caller fills in as it learns things. The record is
    written in `finally`, so a request that raises is logged before the
    exception continues on its way.
    """
    import generate

    before = generate.counters()
    started = time.perf_counter()
    record = {
        "ts": _now(),
        "request_id": new_request_id(),
        "route": route,
        "method": method,
        **fields,
    }

    try:
        yield record
    except Exception as exc:  # noqa: BLE001
        record["outcome"] = "error"
        record["status"] = 500
        record["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        record["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
        after = generate.counters()
        record["model_calls"] = after["calls"] - before["calls"]
        record["prompt_tokens"] = after["prompt_tokens"] - before["prompt_tokens"]
        record["output_tokens"] = after["output_tokens"] - before["output_tokens"]
        record.setdefault("outcome", "answered")
        record.setdefault("status", 200)
        write(record)
