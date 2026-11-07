import os
from functools import lru_cache
from pathlib import Path
from tomllib import load
from typing import Type, TypeVar

from pydantic import BaseModel, SecretStr

ConfigType = TypeVar("ConfigType", bound=BaseModel)

class BotConfig(BaseModel):
    token: SecretStr

@lru_cache
def parse_config_file() -> dict:
    env_token = os.getenv("token")
    if env_token:
        return {"bot": {"token": env_token}}
    
    config_path = Path(__file__).parent.parent.joinpath("settings.toml")
    if not config_path.exists():
        raise ValueError("Could not find settings file and BOT_TOKEN is not set")
    
    with open(config_path, "rb") as file:
        config_data = load(file)
    return config_data

def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    config_dict = parse_config_file()
    if root_key not in config_dict:
        raise ValueError(f"Key {root_key} not found")
    return model.model_validate(config_dict[root_key])