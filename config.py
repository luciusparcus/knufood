import json
import os

# Import configuration
with open("config.json") as f:
    data = json.load(f)

# Configure BOT_ID
bot_id = os.getenv("BOT_ID") if os.getenv("BOT_ID", None) else data["botId"]
