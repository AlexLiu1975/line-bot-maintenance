from flask import Flask, request, render_template, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境變數設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('b//atJcbyZqDabX2cfE0aoKzmJDm1ljckW1HfwqbsX6wJZN+FBXgMqAoDPmT2rj5xL7AXs5zbcfx3p0aW8MEmUs7sezQMsLaNooSyTknCCiDrRbJk3lu76jYWNwAk/BYfXiYlnvqijfNb6BR1pNO5QdB04t89/1O/w1cDnyilFU=')
LINE_CHANNEL_SECRET = os.environ.get('0c0a7f823acdc24d4c3a3c78e2bf09bb')
LINE_GROUP_ID = os.environ.get('2007868235')  # 群組 ID 或使用者 ID

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text
    reply_text = f"你說的是：{user_text}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

@app.route("/submit", methods=['POST'])
def submit():
    data = request.json
    name = data.get('name')
    issue = data.get('issue')
    msg = f"\ud83d\udcc4 維修單\n姓名: {name}\n問題: {issue}"
    try:
        line_bot_api.push_message(LINE_GROUP_ID, TextSendMessage(text=msg))
        return jsonify({"status": "sent"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
