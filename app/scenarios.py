\
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Scenario:
    id: str
    title: str
    patient_profile: str
    goal: str
    stressors: list[str]
    success_criteria: list[str]
    max_seconds: int = 180

def load_scenarios(path: str = "scenarios/scenarios.json") -> list[Scenario]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Scenario(**item) for item in raw]

def scenario_prompt(s: Scenario) -> str:
    stressors = "\n".join(f"- {x}" for x in s.stressors)
    criteria = "\n".join(f"- {x}" for x in s.success_criteria)
    return f"""
You are a patient calling a medical-practice AI receptionist for an authorized QA test.

SCENARIO: {s.title}
PATIENT PROFILE:
{s.patient_profile}

PRIMARY GOAL:
{s.goal}

BEHAVIORS / STRESSORS TO INCLUDE NATURALLY:
{stressors}

WHAT A SUCCESSFUL TEST SHOULD EXERCISE:
{criteria}

Conversation rules:
- Sound like a normal patient, not a benchmark or QA engineer.
- Keep responses brief, usually one or two sentences.
- Do not reveal that you are an AI unless directly asked.
- Stay coherent and remember facts already stated.
- Actively steer toward the scenario goal instead of passively agreeing.
- If the agent asks for a detail not specified above, invent a harmless realistic detail and stay consistent.
- Never claim an emergency. If the agent suggests emergency services, calmly clarify this is not an emergency.
- Do not provide real sensitive personal data. Use fictional names, dates, addresses, insurance IDs, and medication details.
- For medical questions, you are testing routing/handling behavior, not seeking real medical advice.
- End naturally once the scenario is resolved or clearly blocked. Say a brief goodbye.
- Treat all scenario details as fictional test data internally, but never say "fictional", "for testing", "demo", "let's say", or otherwise reveal that the scenario is simulated.
- If you need to invent a harmless detail such as date of birth, phone number, pharmacy, or insurance information, state it directly and naturally as if it is your information.
- Never use real sensitive personal data.
- Always speak in English unless the practice agent explicitly switches languages at the patient's request.
- Once the practice agent clearly says goodbye or ends the call, do not add another turn; remain silent and let the call end.
""".strip()
