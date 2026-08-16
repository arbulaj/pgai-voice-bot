\
import time
import uuid
from pathlib import Path
import requests
from twilio.rest import Client

from .config import settings
from .store import append_event, render_text_transcript

RECORDINGS_DIR = Path("artifacts/recordings")
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

def _validate():
    required = {
        "TWILIO_ACCOUNT_SID": settings.twilio_account_sid,
        "TWILIO_AUTH_TOKEN": settings.twilio_auth_token,
        "TWILIO_FROM_NUMBER": settings.twilio_from_number,
        "OPENAI_API_KEY": settings.openai_api_key,
        "PUBLIC_BASE_URL": settings.public_base_url,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))
    if settings.test_number != "+18054398008":
        raise RuntimeError(
            "Safety check failed: TEST_NUMBER must be exactly +18054398008 for this assessment."
        )

def start_call(scenario_id: str) -> tuple[str, str]:
    _validate()
    run_id = f"{scenario_id}-{uuid.uuid4().hex[:8]}"
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    call = client.calls.create(
        to=settings.test_number,
        from_=settings.twilio_from_number,
        url=f"{settings.public_base_url}/twiml/{run_id}/{scenario_id}",
        method="POST",
        record=True,
        recording_channels="dual",
        recording_status_callback=f"{settings.public_base_url}/status/{run_id}",
        status_callback=f"{settings.public_base_url}/status/{run_id}",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
    )
    append_event(run_id, {"type": "call_created", "call_sid": call.sid, "scenario_id": scenario_id})
    return run_id, call.sid

def wait_for_completion(call_sid: str, timeout_seconds: int = 240):
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    deadline = time.time() + timeout_seconds
    last = None
    while time.time() < deadline:
        call = client.calls(call_sid).fetch()
        last = call.status
        if last in {"completed", "busy", "failed", "no-answer", "canceled"}:
            return last
        time.sleep(3)
    raise TimeoutError(f"Call {call_sid} did not complete in time; last status={last}")

def download_recording(run_id: str, call_sid: str, wait_seconds: int = 90):
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    # First wait for Twilio to create the Recording resource.
    deadline = time.time() + wait_seconds
    recordings = []

    while time.time() < deadline:
        recordings = client.recordings.list(call_sid=call_sid, limit=20)

        if recordings:
            break

        print("[recording] Waiting for recording resource...")
        time.sleep(3)

    if not recordings:
        raise RuntimeError(f"No recording found for {call_sid}")

    rec = recordings[0]

    # A Recording resource can exist before its media file is ready.
    # Wait until Twilio reports the recording as completed.
    while time.time() < deadline:
        rec = client.recordings(rec.sid).fetch()

        print(f"[recording] status={rec.status}")

        if rec.status == "completed":
            break

        time.sleep(3)
    else:
        raise RuntimeError(
            f"Recording {rec.sid} did not become ready within {wait_seconds} seconds."
        )

    # Twilio supports retrieving Recording media by appending .mp3.
    url = (
        f"https://api.twilio.com/2010-04-01/"
        f"Accounts/{settings.twilio_account_sid}/"
        f"Recordings/{rec.sid}.mp3"
    )

    # Retry the media request too, because there can be a short delay between
    # status=completed and the MP3 becoming available.
    media_deadline = time.time() + 30

    while time.time() < media_deadline:
        response = requests.get(
            url,
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
            timeout=60,
        )

        if response.status_code == 200:
            break

        if response.status_code == 404:
            print("[recording] MP3 not ready yet; retrying...")
            time.sleep(3)
            continue

        response.raise_for_status()
    else:
        raise RuntimeError(f"MP3 for recording {rec.sid} never became available.")

    out = RECORDINGS_DIR / f"{run_id}.mp3"
    out.write_bytes(response.content)

    append_event(
        run_id,
        {
            "type": "recording_downloaded",
            "recording_sid": rec.sid,
            "path": str(out),
        },
    )

    render_text_transcript(run_id)

    return out