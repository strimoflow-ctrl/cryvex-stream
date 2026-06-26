from ..config import Telegram
from pyrogram import Client

FileStream = Client(
    name="FileStream",
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    workdir="FileStream",
    plugins={"root": "FileStream/bot/plugins"},
    bot_token=Telegram.BOT_TOKEN,
    sleep_threshold=Telegram.SLEEP_THRESHOLD,
    workers=Telegram.WORKERS
)

multi_clients = {0: FileStream}
work_loads = {0: 0}

