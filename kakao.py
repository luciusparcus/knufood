# -*- coding: utf-8 -*-

from config import bot_id
from menu import Menu, get_available_menus, synchronise_menus

from flask import Flask, request, jsonify
app = Flask(__name__)

from datetime import datetime, timedelta
from threading import Timer


print("Loading menus...")
menus = get_available_menus()
print("Successfully loaded the menus")

# Synchronise data every day at 00:00
x = datetime.today()
y = x.replace(day=x.day, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
t = Timer((y-x).total_seconds(), synchronise_menus)
t.start()
print("Timer set to synchronise data every day at 00:00")


def create_reply(text):
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "{}".format(text)
                    }
                }
            ]
        }
    })


@app.route("/knufood", methods=["POST"])
def knufood():
    data = request.get_json()

    # Return an error if request is sent by an unidentified bot
    if bot_id != data["bot"]["id"]:
        return create_reply("인증되지 않은 요청이 발생하였습니다. 개발자에게 연락하세요.")
    # Return an error if the user has not added the bot
    try:
        data["userRequest"]["user"]["properties"]["isFriend"]
    except KeyError:
        return create_reply("서비스를 이용하시려먼 먼저 채널을 추가해 주세요.")

    command = data["userRequest"]["utterance"]

    # Synchronise data
    if menus[command].is_expired():
        menus[command] = Menu(command, force_retrieve=True, force_dump=True)

    return create_reply(menus[command])
