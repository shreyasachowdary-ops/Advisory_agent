from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "qwen3.8:latest"
    ollama_embed_model: str = "nomic-embed-text"
    chroma_path: str = str(BACKEND_ROOT / "data" / "chroma")
    kb_version: str = "0.1.0"
    school_id: str = "poc_test_school"
    api_host: str = "127.0.0.1"
    api_port: int = 8787
    cors_origins: str = "http://127.0.0.1:43123"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
