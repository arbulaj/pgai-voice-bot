# Loom 1 — Project Walkthrough (target: 2:30–3:00)

Use this as talking points, not a word-for-word script.

## 0:00–0:25 — Problem and goal
- I built an automated patient simulator that makes real calls to the assessment line.
- My first priority was conversational quality because the challenge explicitly grades the calls before the code.
- I also wanted the test suite to produce useful evidence: recordings, transcripts, and traceable bug findings.

## 0:25–1:05 — Architecture
- Show `ARCHITECTURE.md`.
- Twilio makes the outbound call from one fixed number.
- A bidirectional Media Stream sends the practice agent's audio to my FastAPI WebSocket.
- OpenAI Realtime acts as the patient and returns audio directly.
- I use server-side VAD and clear queued Twilio audio on interruption to improve turn-taking.
- Twilio records the actual call in dual-channel mode.

## 1:05–1:45 — Scenario design
- Show `scenarios/scenarios.json`.
- Explain that scenarios have a goal, patient profile, stressors, and success criteria rather than a rigid script.
- Point out a few examples: scheduling, cancellation, refill routing, insurance uncertainty, correction/memory, interruption, multi-intent.
- Explain that this keeps calls realistic while still making each call test a specific behavior.

## 1:45–2:20 — Evidence and iteration
- Show two or three real transcript/recording pairs.
- Play a short snippet from one good call and one problematic call.
- Show the corresponding bug report entry.
- Explain one concrete change you made after early calls, such as VAD timing, patient prompt length, or barge-in handling, and show the before/after effect.

## 2:20–2:50 — Tradeoffs and close
- Realtime speech-to-speech was chosen over STT→LLM→TTS to reduce latency.
- I kept the service local/tunneled instead of deploying production infrastructure because the task rewards a working test harness, not over-engineering.
- The destination is hard-allowlisted so the program cannot dial a different number accidentally.
- Close with the most valuable bug you found and why it matters.
