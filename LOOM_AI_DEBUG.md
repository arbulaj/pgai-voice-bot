# Loom 2 — AI Debugging Demonstration

Do this with your webcam on and record a **real** debugging session. Do not fake a bug after the fact.

A good demo is 2–3 minutes:
1. Run one scenario and show a real failure or awkward behavior.
2. Copy the relevant error/log/code into the AI chat.
3. Ask a focused question that includes your hypothesis.
4. Evaluate the suggestion instead of blindly accepting it.
5. Make the smallest code/config change.
6. Re-run the same scenario or a short test.
7. Explain whether the evidence improved.

Example prompt pattern:
> I'm bridging Twilio bidirectional Media Streams to OpenAI Realtime. During barge-in, the remote agent begins speaking but my patient audio keeps playing for about a second. Here are the relevant WebSocket events and my handler. Identify the likely cause, propose the smallest fix, and tell me what log evidence would confirm the fix. Don't rewrite unrelated code.

What the reviewer should hear from you:
- what you observed,
- what you think caused it,
- why you accepted or rejected the AI suggestion,
- what changed in the result.
