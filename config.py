from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"

    image_provider: str = "huggingface"
    hf_token: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"

    diffusers_model: str = "runwayml/stable-diffusion-v1-5"
    diffusers_steps: int = 25

    image_width: int = 768
    image_height: int = 768

    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return BASE_DIR / "exports"

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return settings