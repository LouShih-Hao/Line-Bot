from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import os
import openai


app = Flask(__name__)

channel_access_token = os.environ['channel_access_token']
channel_secret = os.environ['channel_secret']
openai.api_key = os.environ['openai_api_key']

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)


def GPT_response(text):
    try:
        # Log the request before sending
        print("Sending request to OpenAI API with prompt:", text)
        # 接收回應
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            max_tokens=500,
            temperature=0.5
        )
        # Log the response
        print("Received response from OpenAI API:", response)
        # 重組回應
        answer = response.choices[0].text.strip()
        return answer
    except Exception as e:
        print("Error occurred while requesting from OpenAI API:", e)
        return "抱歉，無法取得回應。請稍後再試。"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        msg = event.message.text
        gpt_answer = GPT_response(msg)
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=gpt_answer)]))


if __name__ == "__main__":
    app.run()
