from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from RiZoeL.VideoStreaming import app


RiZoeL = Client(
    ":memory:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="RiZoeL"),
)

RiZoeL.start()
print("[INFO]: STARTING BOT CLIENT")
app.start()
print("[INFO]: STARTING USERBOT CLIENT")
idle()
