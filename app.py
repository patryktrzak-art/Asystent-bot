import logging
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "TUTAJ_WPISZ_SWÓJ_PRAWDZIWY_TOKEN"
GEMINI_API_KEY = "TUTAJ_WPISZ_SWÓJ_KLUCZ_GEMINI"
CHAT_ID = 9121741673

client = genai.Client(api_key=GEMINI_API_KEY)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Marcin dziala poprawnie!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def generate_ai_content(prompt: str) -> str:
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        try:
            response = client.models.generate_content(model="gemini-flash", contents=prompt)
            return response.text
        except Exception:
            return "Wystąpił problem techniczny."

async def send_daily_report(application):
    prompt = "Przygotuj krótkie, motywujące powitanie na dzisiejszy poranek oraz podaj ciekawostkę."
    text = generate_ai_content(prompt)
    try:
        await application.bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Błąd wysyłania: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_message = update.message.text
        reply_text = generate_ai_content(f"Jesteś pomocnym asystentem o imieniu Marcin. Odpowiedz: {user_message}")
        await update.message.reply_text(reply_text)

def main():
    Thread(target=run_health_check_server, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    scheduler = BackgroundScheduler(timezone="Europe/Warsaw")
    scheduler.add_job(lambda: application.job_queue.run_once(lambda ctx: client.loop.create_task(send_daily_report(application)), 0), 'cron', hour=8, minute=0)
    scheduler.start()
    
    application.run_polling()

if __name__ == "__main__":
    main()
