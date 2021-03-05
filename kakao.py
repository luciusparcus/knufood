from flask import Flask, request, jsonify

from config import bot_id
from menu import Menu

app = Flask(__name__)

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

    # Set the default reply as unknown
    command = data["userRequest"]["utterance"]

    return create_reply(Menu(command))
