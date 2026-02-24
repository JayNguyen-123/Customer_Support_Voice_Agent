import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_name: str = os.getenv("DB_NAME", "")
    db_user: str = os.getenv("DB_USER", "")
    db_password: str = int(os.getenv("DB_PASSWORD", ""))
    db_min_conn: int = int(os.getenv("DB_MIN_CONN", "1"))
    db_max_conn: int = int(os.getenv("DB_MAX_CONN", "5"))

    jira_base: str = os.getenv("JIRA_BASE", "")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")
    jira_project_key: str = os.getenv("JIRA_PROJECT_KEY", "SUPPORT")

    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8765"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
    elevenlabs_api_key: str = os.getenv("ELEVENLABS_API_KEY", "")


settings = Settings()
