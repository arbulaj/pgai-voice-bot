# Pretty Good AI — Patient Voice Bot

Automated Python voice caller for the Pretty Good AI AI Engineering Challenge.

## What it does

- Calls **only** the assessment number `+1-805-439-8008`
- Uses scenario-driven OpenAI Realtime speech-to-speech as the simulated patient
- Streams audio through Twilio bidirectional Media Streams
- Records the real call in dual-channel mode
- Saves two-sided transcripts
- Runs a diverse suite of patient scenarios
- Generates an AI-assisted first pass at a bug report for manual verification

## Safety / scope

The destination is hard-allowlisted. `TEST_NUMBER` must equal `+18054398008`, or the program refuses to place a call.

Use fictional patient information only. Do not put real medical, insurance, or identity data into scenarios or transcripts.

## Project layout

```text
app/
  calls.py       # places calls, polls status, downloads MP3 recordings
  cli.py         # CLI commands
  config.py      # environment configuration
  server.py      # FastAPI + Twilio/OpenAI WebSocket bridge
  scenarios.py   # scenario prompt generation
  store.py       # transcript/event storage
  analyze.py     # AI-assisted bug-report generation
scenarios/
  scenarios.json
artifacts/
  recordings/
  transcripts/
  analysis/
ARCHITECTURE.md
BUG_REPORT.md
LOOM_WALKTHROUGH.md
LOOM_AI_DEBUG.md
```

## Prerequisites

- Python 3.11+
- A Twilio account with one voice-capable phone number
- An OpenAI API key with Realtime access
- A public HTTPS tunnel such as ngrok for the local FastAPI server

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env`.

Fill in:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_FROM_NUMBER`
- `OPENAI_API_KEY`

Keep:

```env
TEST_NUMBER=+18054398008
```

Do **not** commit `.env`.

### 3. Start the app

```bash
python -m app.cli serve
```

Check:

```text
http://localhost:8000/health
```

### 4. Expose port 8000 publicly

Example with ngrok:

```bash
ngrok http 8000
```

Copy the generated HTTPS URL into `.env` as `PUBLIC_BASE_URL`, then restart the app.

Example:

```env
PUBLIC_BASE_URL=https://abc123.ngrok-free.app
```

## Static preflight

Before exposing the server or spending money, run:

```bash
python -m app.cli preflight
```

This checks the scenario count, unique IDs, artifact folders, and the hard-allowlisted assessment number without making a phone call.

## Run a single smoke test first

In a second terminal with the same virtual environment:

```bash
python -m app.cli call 01_simple_schedule
```

Listen to the resulting MP3 in `artifacts/recordings/` and inspect the matching transcript in `artifacts/transcripts/`.

**Do not immediately launch all 10+ calls.** First confirm:
- both sides can hear each other,
- turn-taking sounds natural,
- the transcript contains both speakers,
- the recording downloads successfully.

Then adjust VAD/prompt behavior if necessary.

## Run the suite

The included suite has 12 scenarios. The challenge minimum is 10.


```bash
python -m app.cli suite
```

For exactly the first 10:

```bash
python -m app.cli suite --limit 10
```

The command runs scenarios sequentially and downloads each completed call recording as MP3.

### Assessment runs

For the final assessment, I ran the first 10 scenarios individually so I could review each call before continuing:

```bash
python -m app.cli call 01_simple_schedule
python -m app.cli call 02_reschedule
python -m app.cli call 03_cancel
python -m app.cli call 04_refill
python -m app.cli call 05_hours_location
python -m app.cli call 06_insurance
python -m app.cli call 07_ambiguous_request
python -m app.cli call 08_barge_in
python -m app.cli call 09_correction_memory
python -m app.cli call 10_unusual_constraint
```

Each completed assessment run has a corresponding MP3 recording and text transcript under `artifacts/`.

## Generate an initial bug report

After calls are complete:

```bash
python -m app.cli analyze
```

This creates:

```text
artifacts/analysis/generated_bug_report.md
```

**Manually verify every generated finding against the transcript and audio.** Move only real, useful issues into `BUG_REPORT.md`.

## Realtime compatibility note

OpenAI's Realtime API has changed schemas over time. The app defaults to the current GA-style session configuration and also recognizes both GA and older beta event names. If your account exposes the older session schema, add:

```env
REALTIME_SCHEMA=legacy
```

and restart the server.

## What to inspect after early calls

The highest-value iteration targets are usually:

1. **Latency / pauses** — if turns feel slow, inspect network tunnel latency and VAD timing.
2. **Talking over the agent** — `input_audio_buffer.speech_started` triggers a Twilio `clear` event to stop queued patient audio.
3. **Patient talks too much** — tighten the scenario prompt to one or two sentences per turn.
4. **Patient gives up too easily** — strengthen the scenario goal and success criteria.
5. **Transcript speaker mix-ups** — confirm the Realtime input transcript is the practice-agent side and output transcript is the patient-bot side.

### Iterations made during testing

After reviewing the early calls, I made several targeted changes to the test harness:

- Reduced the server-side VAD silence threshold from 650 ms to 400 ms to improve turn latency.
- Added Realtime event timestamps to diagnose pauses between speakers.
- Improved the patient prompt so fictional information is stated naturally without exposing the test setup.
- Added instructions to keep responses short and conversational.
- Added language and conversation-ending rules to reduce simulator artifacts.
- Improved recording retrieval so the client waits for Twilio recording processing before downloading the MP3.

I kept test-harness problems separate from issues observed in the practice agent. The final manually reviewed findings are documented in `BUG_REPORT.md`.

## GitHub submission checklist

- [x] Public repository
- [x] Working Python code
- [x] `.env.example`
- [x] README
- [x] `ARCHITECTURE.md`
- [x] At least 10 complete transcript files
- [x] Matching MP3/OGG recordings for at least 10 calls
- [x] Manually verified `BUG_REPORT.md`
- [x] Loom #1 public, webcam on, max 3 minutes
- [x] Loom #2 public AI-debugging screen recording, webcam on
- [x] Submission form contains the **single Twilio caller number** in E.164 format
- [x] No API keys or `.env` committed
- [x] Receipts retained if requesting reimbursement
