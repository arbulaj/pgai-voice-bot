\
from pathlib import Path
from .config import settings
from .scenarios import load_scenarios

def run_preflight():
    scenarios = load_scenarios()
    problems = []

    if len(scenarios) < 10:
        problems.append(f"Only {len(scenarios)} scenarios found; challenge requires at least 10.")
    if settings.test_number != "+18054398008":
        problems.append("TEST_NUMBER is not the assessment allowlisted number.")
    ids = [s.id for s in scenarios]
    if len(ids) != len(set(ids)):
        problems.append("Scenario IDs are not unique.")
    if not Path(".env.example").exists():
        problems.append(".env.example is missing.")

    print(f"Scenarios: {len(scenarios)}")
    print(f"Allowlisted destination: {settings.test_number}")
    print("Artifact directories:", Path("artifacts/recordings").exists(),
          Path("artifacts/transcripts").exists(), Path("artifacts/analysis").exists())

    if problems:
        for p in problems:
            print("[FAIL]", p)
        raise SystemExit(1)
    print("[PASS] Static preflight checks passed.")
