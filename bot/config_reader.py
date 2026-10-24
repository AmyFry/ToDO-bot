from functools import lru_cache
from pathlib import Path
from tomllib import load
from typing import Type, TypeVar

from pydantic import BaseModel, SecretStr

ConfigType = TypeVar("ConfigType", bound=BaseModel)

class BotConfig(BaseModel):
    # Выводит текст со звёздочками, если вдруг попытаться print() или в логах вывести.
    token: SecretStr

@lru_cache # [3]
def parse_config_file() -> dict:
    # Формируем путь к файлу settings.toml
    config_path = Path(__file__).parent.parent.joinpath("settings.toml")
    if not config_path.exists():
        error = "Could not find settings file"
        raise ValueError(error)
    # Читаем сам файл и пытаемся прочитать как TOML
    with open (config_path, "rb") as file:
        config_data = load(file)
    return config_data

def get_config(model: Type[ConfigType], root_key: str) -> ConfigType:
    config_dict = parse_config_file()
    if root_key not in config_dict:
        error = f"Key {root_key} not found"
        raise ValueError(error)
    return model.model_validate(config_dict[root_key])