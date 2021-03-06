# -*- coding: utf-8 -*-

import json
import os

# Import configuration
if os.getenv("DYNO", None):
    if os.getenv("BOT_ID", None)
        bot_id = os.getenv("BOT_ID")
else:
    with open("config.json") as f:
        data = json.load(f)
        bot_id = data["botId"]
