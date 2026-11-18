from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID   = 0          # your api_id integer
API_HASH = ""         # your api_hash string

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\n=== SESSION STRING (paste into agent_tg.py) ===")
    print(client.session.save())
    print("================================================\n")
