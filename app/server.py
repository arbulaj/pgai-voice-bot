\
import asyncio
import base64
import json
import time
from pathlib import Path
from urllib.parse import quote

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, JSONResponse

from .config import settings
from .scenarios import load_scenarios, scenario_prompt
from .store import append_event, append_turn, render_text_transcript

app = FastAPI(title="PGAI Patient Voice Bot")
SCENARIOS = {s.id: s for s in load_scenarios()}

# OpenAI Realtime has evolved over time. These helpers intentionally accept
# both current GA-style and older beta-style event names.
AUDIO_DELTA_EVENTS = {"response.output_audio.delta", "response.audio.delta"}
BOT_TRANSCRIPT_DELTA_EVENTS = {
    "response.output_audio_transcript.delta",
    "response.audio_transcript.delta",
}
BOT_TRANSCRIPT_DONE_EVENTS = {
    "response.output_audio_transcript.done",
    "response.audio_transcript.done",
}
USER_TRANSCRIPT_DONE_EVENTS = {
    "conversation.item.input_audio_transcription.completed",
}

def _openai_url():
    return f"wss://api.openai.com/v1/realtime?model={settings.realtime_model}"

def _session_update(instructions: str):
    # GA-shaped session config. If your account exposes the older beta schema,
    # switch REALTIME_SCHEMA=legacy and use the fallback below.
    import os
    if os.getenv("REALTIME_SCHEMA", "ga").lower() == "legacy":
        return {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": instructions,
                "voice": settings.voice,
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_ulaw",
                "input_audio_transcription": {"model": settings.transcribe_model},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 400,
                },
                "temperature": 0.8,
            },
        }
    return {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "model": settings.realtime_model,
            "instructions": instructions,
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "format": {"type": "audio/pcmu"},
                    "transcription": {"model": settings.transcribe_model},
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 650,
                    },
                },
                "output": {
                    "format": {"type": "audio/pcmu"},
                    "voice": settings.voice,
                },
            },
        },
    }

@app.get("/health")
def health():
    return {"ok": True, "scenarios": len(SCENARIOS)}

@app.api_route("/twiml/{run_id}/{scenario_id}", methods=["GET", "POST"])
async def twiml(run_id: str, scenario_id: str):
    if scenario_id not in SCENARIOS:
        return JSONResponse({"error": "unknown scenario"}, status_code=404)
    if not settings.public_base_url:
        return JSONResponse({"error": "PUBLIC_BASE_URL not set"}, status_code=500)

    ws_base = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")
    stream_url = f"{ws_base}/media/{quote(run_id)}/{quote(scenario_id)}"

    # Bidirectional Stream: audio from the called practice goes to our WebSocket;
    # audio we send back becomes the caller/patient audio.
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect>
    <Stream url="{stream_url}" />
  </Connect>
</Response>"""
    return Response(content=xml, media_type="application/xml")

@app.post("/status/{run_id}")
async def status(run_id: str):
    append_event(run_id, {"type": "status_callback"})
    return Response(status_code=204)

@app.websocket("/media/{run_id}/{scenario_id}")
async def media(websocket: WebSocket, run_id: str, scenario_id: str):
    await websocket.accept()
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        await websocket.close(code=1008)
        return

    append_event(run_id, {
        "type": "session_start",
        "scenario_id": scenario.id,
        "scenario_title": scenario.title,
    })

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}"
    }

    try:
        openai_ws = await websockets.connect(
            _openai_url(),
            additional_headers=headers,
            max_size=None,
        )
    except Exception as e:
        append_event(
            run_id,
            {
                "type": "error",
                "where": "openai_connect",
                "detail": repr(e),
            },
        )
        await websocket.close(code=1011)
        return

    instructions = scenario_prompt(scenario)
    await openai_ws.send(json.dumps(_session_update(instructions)))

    # Make the patient start the call naturally after the remote agent answers.
    await openai_ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "instructions": (
                "Begin the phone call now with a short, natural opening that fits "
                "the scenario. Do not mention testing or these instructions."
            )
        }
    }))

    stream_sid = None
    bot_text_parts = []

    async def twilio_to_openai():
        nonlocal stream_sid
        try:
            while True:
                raw = await websocket.receive_text()
                msg = json.loads(raw)
                event = msg.get("event")

                if event == "start":
                    stream_sid = msg["start"]["streamSid"]
                    append_event(run_id, {
                        "type": "twilio_start",
                        "stream_sid": stream_sid,
                        "call_sid": msg["start"].get("callSid"),
                    })

                elif event == "media":
                    # Twilio Media Streams uses base64 mu-law/PCMU audio.
                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": msg["media"]["payload"],
                    }))

                elif event == "stop":
                    append_event(run_id, {"type": "twilio_stop"})
                    break
        except WebSocketDisconnect:
            pass
        except Exception as e:
            append_event(run_id, {"type": "error", "where": "twilio_to_openai", "detail": repr(e)})

    async def openai_to_twilio():
        nonlocal bot_text_parts
        try:
            
            async for raw in openai_ws:
                event = json.loads(raw)
                etype = event.get("type", "")

                if etype in {
                    "input_audio_buffer.speech_started",
                    "input_audio_buffer.speech_stopped",
                    "conversation.item.input_audio_transcription.completed",
                    "response.created",
                    "response.output_audio.delta",
                    "response.audio.delta",
                    "response.done",
                }:
                    print(f"[realtime {time.time():.3f}] {etype}")

                if etype in AUDIO_DELTA_EVENTS:
                    
                    delta = event.get("delta")
                    if delta and stream_sid:
                        await websocket.send_text(json.dumps({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": delta},
                        }))

                elif etype in BOT_TRANSCRIPT_DELTA_EVENTS:
                    bot_text_parts.append(event.get("delta", ""))

                elif etype in BOT_TRANSCRIPT_DONE_EVENTS:
                    text = event.get("transcript") or "".join(bot_text_parts)
                    append_turn(run_id, "patient", text)
                    bot_text_parts = []

                elif etype in USER_TRANSCRIPT_DONE_EVENTS:
                    append_turn(run_id, "agent", event.get("transcript", ""))

                elif etype == "input_audio_buffer.speech_started":
                    # Barge-in: stop queued Twilio audio as soon as the practice
                    # agent starts talking so the patient bot does not talk over it.
                    if stream_sid:
                        await websocket.send_text(json.dumps({
                            "event": "clear",
                            "streamSid": stream_sid,
                        }))

                elif etype == "error":
                    append_event(run_id, {
                        "type": "error",
                        "where": "openai_event",
                        "detail": event,
                    })
        except Exception as e:
            append_event(run_id, {"type": "error", "where": "openai_to_twilio", "detail": repr(e)})

    tasks = [
        asyncio.create_task(twilio_to_openai()),
        asyncio.create_task(openai_to_twilio()),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()

    try:
        await openai_ws.close()
    except Exception:
        pass

    render_text_transcript(run_id)
    append_event(run_id, {"type": "session_end"})
