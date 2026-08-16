\
from pathlib import Path
from openai import OpenAI
from .config import settings

TRANSCRIPTS = Path("artifacts/transcripts")
OUT = Path("artifacts/analysis/generated_bug_report.md")
OUT.parent.mkdir(parents=True, exist_ok=True)

SYSTEM = """You are a QA analyst evaluating a medical-practice voice AI from authorized test-call transcripts.
Find only substantive product bugs or quality problems. Prioritize incorrect commitments, unsafe handling,
contradictions, failure to respect business constraints, broken state/memory, poor routing, hallucinated
information, and severe conversational failures. Do not invent facts that are not in the transcript.
For each issue include severity, call/transcript filename, a short evidence excerpt, why it matters, and expected behavior.
Also include a section for calls where no meaningful bug was found. Be concise and specific."""

def build_bug_report():
    client = OpenAI(api_key=settings.openai_api_key)
    chunks = []
    for path in sorted(TRANSCRIPTS.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            chunks.append(f"### {path.name}\n{text}")
    if not chunks:
        raise RuntimeError("No transcript .txt files found in artifacts/transcripts.")

    prompt = SYSTEM + "\n\nTRANSCRIPTS:\n\n" + "\n\n".join(chunks)
    resp = client.responses.create(
        model=settings.analysis_model,
        input=prompt,
    )
    report = resp.output_text
    header = (
        "# Generated Bug Report\n\n"
        "> AI-assisted first pass. Manually verify every issue against the audio before submission.\n\n"
    )
    OUT.write_text(header + report + "\n", encoding="utf-8")
    return OUT
