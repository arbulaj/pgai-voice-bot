
# Pretty Good AI — Patient Voice Bot

**Real-time AI voice testing platform built with Python, FastAPI, Twilio, and OpenAI Realtime**

A Python-based voice testing system that simulates patients in live phone conversations with a healthcare scheduling assistant. The application places authorized test calls, streams two-way audio, saves recordings and transcripts, and supports scenario-based testing and bug analysis.

I built this project for an AI engineering challenge to evaluate how a conversational healthcare assistant handles realistic patient requests, interruptions, corrections, and unusual constraints.

## Project Highlights

- Built a real-time voice application connecting **Twilio Media Streams** with **OpenAI Realtime** through a **FastAPI WebSocket server**.
- Created scenario-driven AI patients to test healthcare scheduling and administrative workflows.
- Completed and reviewed **10 assessment calls**, with matching audio recordings and transcripts.
- Added event instrumentation to investigate pauses and turn-taking problems.
- Improved test-harness responsiveness by tuning voice activity detection (VAD) and interruption handling.
- Documented manually verified issues in a bug report, separating problems in the test harness from issues observed in the assistant being evaluated.
- Implemented a hard allowlist so the application can call only the authorized assessment number.

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python, FastAPI |
| Real-time communication | WebSockets, Twilio bidirectional Media Streams |
| Conversational AI | OpenAI Realtime API |
| Testing | Scenario-driven calls, audio review, transcript analysis |
| Observability | Realtime event timestamps, call artifacts, bug reports |
| Development | Git, GitHub, Windows PowerShell |

## How It Works

The application acts as a simulated patient during a live phone call.

1. A test scenario defines the patient's request, fictional details, and conversational goal.
2. The application places a call to the authorized assessment number using Twilio.
3. Twilio streams audio between the phone call and the FastAPI server.
4. The server bridges the audio stream to OpenAI Realtime, which generates the simulated patient's spoken responses.
5. The application stores transcripts and call events and retrieves the completed call recording.
6. I review the artifacts to identify conversational failures, unexpected behavior, and opportunities to improve the test system.

```text
Scenario configuration
        |
        v
Python CLI / call manager
        |
        v
Twilio phone call
        |
        v
Bidirectional Media Stream
        |
        v
FastAPI WebSocket bridge
        |
        v
OpenAI Realtime
        |
        v
Simulated patient responses

Call artifacts:
recordings + transcripts + events
        |
        v
Manual review + bug report
```

For additional implementation details, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Testing and Scenarios

I completed the following **10 assessment scenarios**, reviewing each call before continuing to the next:

| Scenario | What it tested |
| --- | --- |
| Appointment scheduling | A straightforward scheduling request |
| Rescheduling | Changing an existing appointment |
| Cancellation | Canceling an appointment |
| Prescription refill | Handling a refill-related request |
| Hours and location | Answering administrative questions |
| Insurance | Responding to insurance-related questions |
| Ambiguous request | Clarifying an unclear patient goal |
| Barge-in | Handling an interruption while speaking |
| Correction and memory | Responding when the patient corrects earlier information |
| Unusual constraint | Handling a less typical patient requirement |

Each completed assessment run produced a corresponding recording and transcript under `artifacts/`.

### What I Reviewed

I listened to the calls and inspected transcripts for:

- Whether the assistant understood the patient's request.
- Whether it maintained context when the patient corrected information.
- How it handled interruptions and ambiguous requests.
- Whether responses were conversational and appropriately timed.
- Whether unexpected behavior could be reproduced and documented.

The final manually reviewed findings are in [`BUG_REPORT.md`](BUG_REPORT.md).

## Engineering Challenges and Improvements

### 1. Reducing response latency

Early test calls exposed noticeable pauses between conversational turns. I added Realtime event timestamps to investigate where delays occurred and reduced the server-side VAD silence threshold from **650 ms to 400 ms**.

This helped make the simulated patient more responsive during later calls.

### 2. Handling interruptions

Real phone conversations do not always follow a strict turn-taking pattern. I improved interruption handling so a speech-start event can trigger a Twilio `clear` message, stopping queued patient audio when the other speaker begins talking.

### 3. Improving simulated-patient behavior

I revised scenario prompts to make the simulated patient:

- Speak naturally and concisely.
- Stay focused on the scenario goal.
- Provide fictional information conversationally.
- Avoid exposing the underlying test setup.
- Follow more consistent conversation-ending behavior.

### 4. Making call artifacts reliable

I improved recording retrieval so the application waits for Twilio to finish processing a recording before downloading the MP3.

I also kept transcripts and recordings organized by scenario to make manual review easier.

### 5. Separating test-harness bugs from assistant bugs

An important part of this project was distinguishing failures caused by **my testing system** from failures in the **healthcare assistant being tested**.

I used audio, transcripts, and event data to investigate observed behavior before including findings in the final report.

## Repository Structure

```text
app/
  calls.py       # Call placement, status polling, recording retrieval
  cli.py         # Command-line interface
  config.py      # Environment configuration
  server.py      # FastAPI and Twilio/OpenAI WebSocket bridge
  scenarios.py   # Scenario prompt generation
  store.py       # Transcript and event storage
  analyze.py     # AI-assisted initial bug-report generation

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

## Documentation and Demonstrations

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — System design and technical architecture.
- [`BUG_REPORT.md`](BUG_REPORT.md) — Manually reviewed testing findings.
- [`LOOM_WALKTHROUGH.md`](LOOM_WALKTHROUGH.md) — Project walkthrough information.
- [`LOOM_AI_DEBUG.md`](LOOM_AI_DEBUG.md) — AI-assisted debugging walkthrough information.

## Running the Project

**This repository is an assessment-specific test harness, not a general-purpose outbound calling application.** It is restricted to the authorized assessment destination and uses fictional patient information.

### Prerequisites

- Python 3.11+
- A Twilio account and voice-capable number
- An OpenAI API key with Realtime access
- A public HTTPS tunnel for the local FastAPI server

### Install

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure the required credentials and public server URL. **Do not commit `.env` or API keys.**

### Start the server

```powershell
python -m app.cli serve
```

The local health endpoint is:

```text
http://localhost:8000/health
```

### Run the static preflight

```powershell
python -m app.cli preflight
```

This checks the scenario configuration, artifact directories, and destination allowlist without placing a call.

The CLI also supports individual authorized scenario runs and sequential suite execution. See the source code and scenario configuration for the available commands.

## Safety and Data Handling

- Outbound calls are restricted to the hard-allowlisted assessment number.
- Scenarios use fictional patient information.
- Real medical, insurance, and identity information should not be placed in prompts or transcripts.
- Credentials are supplied through environment variables and should never be committed to GitHub.
- AI-generated bug-report drafts require manual verification against the recording and transcript.

## What This Project Demonstrates

This project gave me hands-on experience with **real-time API integration, asynchronous Python services, WebSocket communication, voice AI, scenario-based testing, debugging, event instrumentation, and technical documentation**.

It also strengthened my ability to build a system, test it against realistic workflows, investigate unexpected behavior, and turn the results into actionable engineering findings.
