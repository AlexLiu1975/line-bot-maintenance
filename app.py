from flask import Flask, request, render_template, jsonify
from datetime import datetime
import os
import requests

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# 前端報修表單頁面
@app.route("/", methods=["GET"])
def index():
    location = request.args.get("location", "")
    equipment = request.args.get("equipment", "")
    return render_template("index.html", location=location, equipment=equipment)

# 處理報修表單 POST
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "資料錯誤"})

    msg = format_line_message(data)
    success = send_line_message(msg)
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "發送到 LINE 失敗"})

# 發送訊息到 LINE 群組
def send_line_message(msg):
    token = os.getenv("b//atJcbyZqDabX2cfE0aoKzmJDm1ljckW1HfwqbsX6wJZN+FBXgMqAoDPmT2rj5xL7AXs5zbcfx3p0aW8MEmUs7sezQMsLaNooSyTknCCiDrRbJk3lu76jYWNwAk/BYfXiYlnvqijfNb6BR1pNO5QdB04t89/1O/w1cDnyilFU=")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    to = os.getenv("U13ec8729a0ec07db338b59b731fc0cd9")
    body = {
        "to": to,
        "messages": [{
            "type": "text",
            "text": msg
        }]
    }

    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body)
    return res.status_code == 200

# 處理 LINE Webhook 事件
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    print("📩 收到 Webhook：", body)

    try:
        events = body.get("events", [])
        for event in events:
            source = event.get("source", {})
            print("🔍 Source:", source)

            if source.get("type") == "group":
                group_id = source.get("groupId")
                print("✅ 群組 ID：", group_id)

            elif source.get("type") == "user":
                print("👤 這是個人訊息，不是群組")

    except Exception as e:
        print("Webhook 錯誤：", e)

    return "OK", 200


# 整理 LINE 訊息格式
def format_line_message(data):
    icon = {"緊急": "🚨", "一般": "⚠️", "低": "📝"}.get(data.get["priority"], "📌")
    return f"""{icon} 設備故障報修

📍 位置：{data['location']}
⚙️ 設備：{data['equipment']}
🔧 類別：{data['category']}
⏰ 緊急程度：{data['priority']}
📝 故障描述：{data['description']}
👤 報修人：{data.get('reporter', '未提供')}
📞 聯絡方式：{data.get('contact', '未提供')}
🕐 時間：{data['timestamp']}"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 會提供 PORT 環境變數
    app.run(host="0.0.0.0", port=port)

