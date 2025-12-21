from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    shetran_executable: Optional[str] = None
    shetran_prepare_executable: Optional[str] = None
    calibrated_timeout: Optional[int] = -1

    class Config:
        env_file = ".env"

def create_settings():
    with open(".env", "w") as f:
        f.write("")