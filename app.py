from flask import Flask, request, render_template, jsonify
from datetime import datetime
import os
import requests

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    location = request.args.get("location", "")
    equipment = request.args.get("equipment", "")
    return render_template("index.html", location=location, equipment=equipment)

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

def send_line_message(msg):
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    to = os.getenv("LINE_GROUP_ID")
    body = {
        "to": to,
        "messages": [{
            "type": "text",
            "text": msg
        }]
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body)
    return res.status_code == 200

def format_line_message(data):
    icon = {"緊急": "🚨", "一般": "⚠️", "低": "📝"}.get(data["priority"], "📌")
    return f"""{icon} 設備故障報修

📍 位置：{data['location']}
⚙️ 設備：{data['equipment']}
🔧 類別：{data['category']}
⏰ 緊急程度：{data['priority']}
📝 故障描述：{data['description']}
👤 報修人：{data.get('reporter', '未提供')}
📞 聯絡方式：{data.get('contact', '未提供')}
🕐 時間：{data['timestamp']}"""

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    print("📩 收到 Webhook：", body)
    try:
        events = body.get("events", [])
        for event in events:
            source = event.get("source", {})
            if source.get("type") == "group":
                group_id = source.get("groupId")
                print("✅ 群組 ID：", group_id)
    except Exception as e:
        print("Webhook 處理錯誤：", e)
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)
