\
from pathlib import Path
from datetime import datetime, timezone
import json
import threading

BASE = Path("artifacts")
TRANSCRIPTS = BASE / "transcripts"
TRANSCRIPTS.mkdir(parents=True, exist_ok=True)

_lock = threading.Lock()

def _now():
    return datetime.now(timezone.utc).isoformat()

def append_event(run_id: str, event: dict):
    record = {"ts": _now(), **event}
    path = TRANSCRIPTS / f"{run_id}.jsonl"
    with _lock:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

def append_turn(run_id: str, speaker: str, text: str):
    text = (text or "").strip()
    if not text:
        return
    append_event(run_id, {"type": "turn", "speaker": speaker, "text": text})

def render_text_transcript(run_id: str):
    src = TRANSCRIPTS / f"{run_id}.jsonl"
    dst = TRANSCRIPTS / f"{run_id}.txt"
    lines = []
    if src.exists():
        for line in src.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") == "turn":
                who = "PATIENT BOT" if e.get("speaker") == "patient" else "PRACTICE AGENT"
                lines.append(f"{who}: {e.get('text','').strip()}")
    dst.write_text("\n\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return dst
