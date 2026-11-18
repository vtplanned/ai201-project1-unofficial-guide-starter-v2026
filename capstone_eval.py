#!/usr/bin/env python3
"""
Capstone test harness — runs the trials for unit 9's criteria.

    python capstone_eval.py --label before --trials 3

Each trial sends a fixed request set to a running server, then reads the log
records that request set produced and measures six things. Which five of them
are criteria is decided in criteria.md; this just produces the numbers.

Questions are distinct across every trial on purpose. `generate.py` caches by
prompt, so asking the same question twice would cost zero API calls the second
time and quietly make the cost and call-count numbers meaningless.

Measures, per trial:
  records_per_request  one log record per request, or not
  fields_complete      every record carries the required field set
  failures_logged      the 400s left records behind
  calls_accurate       every answered, uncached /ask logged exactly 1 call
  warm_latency         durations of the answered requests
  tokens_per_run       prompt+output tokens on answered requests
"""

import argparse
import json
import subprocess
import tempfile
import time
from pathlib import Path

LOG = Path("logs/requests.jsonl")
REQUIRED = {"ts", "request_id", "route", "method", "outcome", "status", "duration_ms"}
ASK_FIELDS = {"question", "answer_chars", "refused", "best_distance", "sources",
              "model_calls", "prompt_tokens", "output_tokens"}

# Three distinct in-corpus questions per trial, none repeated across trials.
ANSWERABLE = [
    ["What is the printing quota?",
     "How noisy is Aldridge Hall?",
     "When is the add drop deadline?"],
    ["What are the library hours?",
     "How do I appeal a grade?",
     "What is the workload for PHYS 130?"],
    ["How much does laundry cost in Fenwick Court?",
     "Are CS 340 exams curved?",
     "What time does North Kitchen close?"],
    ["How do I request a transcript?",
     "What is the pass fail deadline?",
     "How noisy is Calder Annexe?"],
]
REFUSABLE = ["What is the capital of Mongolia?", "Who won the 1994 World Cup?"]
MALFORMED = ['{}', 'not json at all']


def post(url, body):
    subprocess.run(
        ["curl", "-s", "--noproxy", "*", "-m", "120", "-o", "/dev/null",
         "-X", "POST", f"{url}/ask", "-H", "Content-Type: application/json",
         "-d", body],
        check=False, capture_output=True,
    )


def get_health(url):
    subprocess.run(["curl", "-s", "--noproxy", "*", "-m", "60", "-o", "/dev/null",
                    f"{url}/health"], check=False, capture_output=True)


CONCURRENT = ["What is the printing quota?",
              "How noisy is Aldridge Hall?",
              "When is the add drop deadline?"]


def post_async(url, body, out):
    """Start a request without waiting for it — criterion 4 needs overlap."""
    return subprocess.Popen(
        ["curl", "-s", "--noproxy", "*", "-m", "120", "-o", out,
         "-X", "POST", f"{url}/ask", "-H", "Content-Type: application/json",
         "-d", body],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def run_concurrent(url, tmpdir):
    """Criterion 4: three /ask requests in flight at once, from separate clients.

    Returns (responses, rows) where rows are the log records matched back to
    each response by request_id, which is what the criterion asks for.
    """
    procs, outs = [], []
    for i, q in enumerate(CONCURRENT):
        out = str(Path(tmpdir) / f"c{i}.json")
        outs.append(out)
        procs.append(post_async(url, json.dumps({"question": q}), out))
    for pr in procs:
        pr.wait()
    time.sleep(0.5)

    responses = []
    for out in outs:
        try:
            responses.append(json.loads(Path(out).read_text()))
        except Exception:
            responses.append({})

    by_id = {r.get("request_id"): r for r in read_log()}
    rows = [by_id.get(resp.get("request_id")) for resp in responses]
    return responses, rows


def measure_concurrent(responses, rows):
    ok = sum(1 for r in responses if r.get("refused") is False)
    matched = [r for r in rows if r]
    accurate = sum(1 for r in matched if r.get("model_calls") == 1)
    return {
        "concurrent_200s": f"{ok}/{len(responses)}",
        "concurrent_rows_matched": f"{len(matched)}/{len(responses)}",
        "concurrent_calls_accurate": f"{accurate}/{len(matched) or len(responses)}",
        "concurrent_calls_seen": [r.get("model_calls") if r else None for r in rows],
    }


def read_log():
    if not LOG.exists():
        return []
    return [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]


def run_trial(url, n):
    """Send one request set. Returns (requests_sent, new_records)."""
    before = len(read_log())
    sent = 0

    for q in ANSWERABLE[n % len(ANSWERABLE)]:
        post(url, json.dumps({"question": q})); sent += 1
    for q in REFUSABLE:
        post(url, json.dumps({"question": q})); sent += 1
    for body in MALFORMED:
        post(url, body); sent += 1
    get_health(url); sent += 1

    time.sleep(0.4)
    return sent, read_log()[before:]


def measure(sent, records):
    answered = [r for r in records if r["outcome"] == "answered" and r["route"] == "/ask"]
    uncached = [r for r in answered if r["model_calls"] > 0 or r["prompt_tokens"] > 0]
    failures = [r for r in records if r["outcome"] in ("bad_request", "error")]
    asks = [r for r in records if r["route"] == "/ask"]

    complete = sum(
        1 for r in records
        if REQUIRED <= set(r) and (r["route"] != "/ask" or r["outcome"] in ("bad_request", "error") or ASK_FIELDS <= set(r))
    )
    accurate = sum(1 for r in uncached if r["model_calls"] == 1)
    lat = sorted(r["duration_ms"] for r in answered)
    toks = [r["prompt_tokens"] + r["output_tokens"] for r in uncached]

    return {
        "requests_sent": sent,
        "records_written": len(records),
        "records_per_request": f"{len(records)}/{sent}",
        "fields_complete": f"{complete}/{len(records)}",
        "failures_logged": f"{len(failures)}/{len(MALFORMED)}",
        "calls_accurate": f"{accurate}/{len(uncached)}",
        "median_latency_ms": round(lat[len(lat) // 2], 1) if lat else None,
        "max_latency_ms": round(lat[-1], 1) if lat else None,
        "mean_tokens": round(sum(toks) / len(toks), 1) if toks else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://127.0.0.1:5055")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--label", default="before")
    args = ap.parse_args()

    print(f"Capstone harness — {args.trials} trials against {args.url}\n")
    rows = []
    for n in range(args.trials):
        print(f"  trial {n + 1} ...", flush=True)
        sent, recs = run_trial(args.url, n)
        row = measure(sent, recs)
        with tempfile.TemporaryDirectory() as td:
            resp, crows = run_concurrent(args.url, td)
        row.update(measure_concurrent(resp, crows))
        rows.append(row)

    keys = ["records_per_request", "fields_complete", "failures_logged",
            "concurrent_200s", "concurrent_calls_accurate", "concurrent_calls_seen",
            "median_latency_ms", "max_latency_ms", "mean_tokens"]
    print(f"\n| Measure | " + " | ".join(f"Trial {i+1}" for i in range(len(rows))) + " |")
    print("|---" * (len(rows) + 1) + "|")
    for k in keys:
        print(f"| {k} | " + " | ".join(str(r[k]) for r in rows) + " |")

    out = Path(f"results/capstone_{args.label}.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2))
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
