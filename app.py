import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai

# 設置 Line 機器人的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
LINE_CHANNEL_SECRET = "YOUR_CHANNEL_SECRET"

# 設置 OpenAI API 密鑰
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# 初始化 Line 相關物件
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化 OpenAI
openai.api_key = OPENAI_API_KEY

# 定義 Line Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 定義 Line 訊息事件處理函式
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    # 使用 OpenAI 聊天模型進行回覆
    response = openai.Completion.create(
        engine="davinci", prompt=user_input, max_tokens=50
    )
    reply = response.choices[0].text.strip()
    # 回覆用戶訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
