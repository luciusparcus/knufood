import json

with open("config.json") as f:
    data = json.load(f)

bot_id = data["botId"]