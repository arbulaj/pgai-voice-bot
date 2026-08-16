\
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    realtime_model: str = os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime")
    analysis_model: str = os.getenv("OPENAI_ANALYSIS_MODEL", "gpt-5-mini")
    transcribe_model: str = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
    voice: str = os.getenv("OPENAI_VOICE", "marin")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    test_number: str = os.getenv("TEST_NUMBER", "+18054398008")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

settings = Settings()
