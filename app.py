import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage

app = Flask(__name__)

# Set up your LINE Bot credentials
channel_secret = 'YOUR_CHANNEL_SECRET'
channel_access_token = 'YOUR_CHANNEL_ACCESS_TOKEN'

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    image_message = event.message
    image_content = line_bot_api.get_message_content(image_message.id)
    
    # Retrieve the content type of the image
    content_type = image_content.headers['Content-Type']
    
    # Save the image locally
    if content_type.startswith('image'):
        filename = f"image_{image_message.id}.jpg"
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'wb') as f:
            for chunk in image_content.iter_content():
                f.write(chunk)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'画像を受け取りました。保存しました: {filename}')
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='画像の受け取りに失敗しました')
        )

@app.route("/", methods=['GET'])
def home():
    return "<h3>Welcome to the homepage!</h3>"


if __name__ == "__main__":
    app.run()
