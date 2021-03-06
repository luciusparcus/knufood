from config import bot_id
from menu import Menu

from flask import Flask, request, jsonify
app = Flask(__name__)

print("Loading menus...")
menus = {
    "누리관": Menu("누리관"),
    "감꽃푸드코트": Menu("감꽃푸드코트"),
    "공학관교직원식당": Menu("공학관교직원식당"),
    "공학관학생식당": Menu("공학관학생식당"),
    "복지관": Menu("복지관"),
    "복현카페테리아": Menu("복현카페테리아"),
    "정보센터식당": Menu("정보센터식당"),
    "카페테리아첨성": Menu("카페테리아첨성")
}
print("Successfully loaded menus")



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
        menus[command] = Menu(command)

    return create_reply(menus[command])


