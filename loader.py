from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils.api_client import TaskManagementAPI
from config import load_config

config = load_config()
storage = MemoryStorage()
bot = Bot(token=config.bot_token)
dp = Dispatcher(storage=storage)
api = TaskManagementAPI(
    base_url=f"http://{config.api_host}:{config.api_port}"
)