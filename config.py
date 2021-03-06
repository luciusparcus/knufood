# -*- coding: utf-8 -*-

import json
import os

# Import configuration
if not os.getenv("DYNO", None):
    with open("config.json") as f:
        data = json.load(f)

# Configure BOT_ID
bot_id = os.getenv("BOT_ID") if os.getenv("BOT_ID", None) else data["botId"]
