from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('b//atJcbyZqDabX2cfE0aoKzmJDm1ljckW1HfwqbsX6wJZN+FBXgMqAoDPmT2rj5xL7AXs5zbcfx3p0aW8MEmUs7sezQMsLaNooSyTknCCiDrRbJk3lu76jYWNwAk/BYfXiYlnvqijfNb6BR1pNO5QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0c0a7f823acdc24d4c3a3c78e2bf09bb')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    reply = f'你剛剛說了：{msg}'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
