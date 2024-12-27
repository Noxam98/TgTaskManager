from dataclasses import dataclass
from environs import Env

@dataclass
class Config:
    bot_token: str
    api_host: str
    api_port: str

def load_config():
    env = Env()
    env.read_env()

    return Config(
        bot_token=env.str("BOT_TOKEN"),
        api_host=env.str("API_HOST", "localhost"),
        api_port=env.str("API_PORT", "8000")
    )
