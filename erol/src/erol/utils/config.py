from __future__ import annotations

from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
	"""Application configuration loaded from environment variables or .env.

	This keeps secrets and environment-specific parameters outside of code.
	"""

	binance_api_key: str | None = Field(default=None, env="BINANCE_API_KEY")
	binance_api_secret: str | None = Field(default=None, env="BINANCE_API_SECRET")
	redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
	data_dir: str = Field(default="./data", env="DATA_DIR")
	environment: str = Field(default="dev", env="ENVIRONMENT")

	class Config:
		env_file = ".env"
		extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	"""Return cached settings instance."""
	return Settings()

