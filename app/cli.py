\
import argparse
import subprocess
import sys
import time

from .calls import start_call, wait_for_completion, download_recording
from .scenarios import load_scenarios
from .analyze import build_bug_report
from .preflight import run_preflight

def run_one(scenario_id: str):
    run_id, call_sid = start_call(scenario_id)
    print(f"[call] {run_id} -> {call_sid}")
    status = wait_for_completion(call_sid)
    print(f"[status] {status}")
    if status == "completed":
        path = download_recording(run_id, call_sid)
        print(f"[recording] {path}")
    return run_id, status

def run_suite(limit: int | None = None):
    scenarios = load_scenarios()
    if limit:
        scenarios = scenarios[:limit]
    results = []
    for i, scenario in enumerate(scenarios, start=1):
        print(f"\n=== {i}/{len(scenarios)}: {scenario.id} — {scenario.title} ===")
        try:
            results.append((scenario.id, *run_one(scenario.id)))
        except Exception as e:
            print(f"[error] {scenario.id}: {e}", file=sys.stderr)
        if i < len(scenarios):
            time.sleep(4)
    return results

def main():
    p = argparse.ArgumentParser(description="Pretty Good AI patient voice-bot challenge")
    sub = p.add_subparsers(dest="cmd", required=True)

    serve = sub.add_parser("serve")
    serve.add_argument("--reload", action="store_true")

    one = sub.add_parser("call")
    one.add_argument("scenario_id")

    suite = sub.add_parser("suite")
    suite.add_argument("--limit", type=int)

    sub.add_parser("analyze")
    sub.add_parser("preflight")

    args = p.parse_args()

    if args.cmd == "serve":
        cmd = ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
        if args.reload:
            cmd.append("--reload")
        raise SystemExit(subprocess.call(cmd))
    elif args.cmd == "call":
        run_one(args.scenario_id)
    elif args.cmd == "suite":
        run_suite(args.limit)
    elif args.cmd == "analyze":
        print(build_bug_report())
    elif args.cmd == "preflight":
        run_preflight()

if __name__ == "__main__":
    main()
