from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction
)
from linebot.exceptions import InvalidSignatureError
from google import genai
from google.genai import types
import os
import logging
from dotenv import load_dotenv

# ตั้งค่า Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

# ตรวจสอบว่ามีค่าใน Environment Variables หรือไม่
line_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
line_secret = os.environ.get("LINE_CHANNEL_SECRET")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

if not all([line_access_token, line_secret, gemini_api_key]):
    logger.error("Missing environment variables. Please check your .env file.")
    exit(1)

line_bot_api = LineBotApi(line_access_token)
handler = WebhookHandler(line_secret)
gemini_client = genai.Client(api_key=gemini_api_key)

SYSTEM_PROMPT = """คุณคือ "นายดี" ผู้ช่วยด้านกฎหมายไทย
เชี่ยวชาญเรื่องสิทธิ์ของประชาชนไทยทั่วไป
ตอบเป็นภาษาไทยเข้าใจง่าย บอก action plan ชัดเจนทีละขั้น
ทุกคำตอบต้องจบด้วย disclaimer สั้นๆ ว่าเป็นข้อมูลเบื้องต้น ไม่ใช่คำแนะนำทางกฎหมายอย่างเป็นทางการ"""

# Quick reply จากข้อมูล Facebook ที่พบบ่อยที่สุด
QUICK_REPLIES = QuickReply(items=[
    QuickReplyButton(action=MessageAction(
        label="🦈 ถูกทวงหนี้ผิดกฎหมาย",
        text="ถูกทวงหนี้ผิดกฎหมาย โทรมาขู่ทำให้อับอาย ผมมีสิทธิ์ทำอะไรได้บ้าง?"
    )),
    QuickReplyButton(action=MessageAction(
        label="💸 ไม่ได้รับเงินที่ตกลงไว้",
        text="ตกลงซื้อขายกันแล้วแต่อีกฝ่ายไม่จ่ายเงิน หรือไม่ส่งของตามสัญญา ทำยังไงได้บ้าง?"
    )),
    QuickReplyButton(action=MessageAction(
        label="🏠 ปัญหามรดกและที่ดิน",
        text="มีปัญหาเรื่องมรดกหรือที่ดิน ผู้จัดการมรดกไม่แบ่งให้ยุติธรรม ทำยังไงได้บ้าง?"
    )),
    QuickReplyButton(action=MessageAction(
        label="⚖️ ถามเรื่องอื่น",
        text="อยากถามเรื่องกฎหมายอื่นๆ"
    )),
])

WELCOME_MESSAGE = """สวัสดีครับ! ผมนายดี 👋
ผู้ช่วยด้านกฎหมายไทยที่พูดภาษาคนธรรมดา

พิมพ์ปัญหาของคุณได้เลย หรือเลือกหัวข้อที่เจอบ่อยด้านล่างครับ 👇"""

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    if not signature:
        logger.warning("X-Line-Signature is missing.")
        abort(400)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # Welcome message เมื่อพิมพ์ครั้งแรกหรือ greeting
    greetings = ["สวัสดี", "หวัดดี", "hello", "hi", "เริ่ม", "start"]
    if any(g in user_message.lower() for g in greetings):
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=WELCOME_MESSAGE,
                    quick_reply=QUICK_REPLIES
                )
            )
        except Exception as e:
            logger.error(f"Line Reply Welcome Error: {e}")
        return

    try:
        max_tokens = int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", 8192))
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=max_tokens,
            ),
        )
        reply = response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        reply = "ขออภัยครับ ขณะนี้ระบบประมวลผลขัดข้อง กรุณาลองใหม่อีกครั้งในภายหลัง"

    try:
        # LINE limits text messages to 5000 characters. Split the reply into chunks of 4900 characters.
        limit = 4900
        chunks = [reply[i:i+limit] for i in range(0, len(reply), limit)][:5]
        messages = []
        for idx, chunk in enumerate(chunks):
            if idx == len(chunks) - 1:
                messages.append(TextSendMessage(text=chunk, quick_reply=QUICK_REPLIES))
            else:
                messages.append(TextSendMessage(text=chunk))
        
        line_bot_api.reply_message(
            event.reply_token,
            messages
        )
    except Exception as e:
        logger.error(f"Line Reply Error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)