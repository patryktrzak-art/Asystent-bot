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

TELEGRAM_TOKEN = "9156443262:AAHz5yAYZmo1KNhNbnh8PXP2RLzb5bxpqG8"
GEMINI_API_KEY = "AQ.Ab8RN6Jddtu1H0apvHAdBvoVmzbUyeQ1fL_kV2_gi5wn2VIdaQ"
CHAT_ID = 9121741673

client = genai.Client(api_key=GEMINI_API_KEY)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Marcin dziala!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def generate_ai_content(prompt: str) -> str:
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        logger.error(f"Błąd Gemini: {e}")
        try:
            response = client.models.generate_content(model="gemini-flash", contents=prompt)
            return response.text
        except Exception as e2:
            logger.error(f"Błąd zapasowy: {e2}")
            return f"Błąd AI: {str(e)[:80]}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_message = update.message.text
        logger.info(f"Otrzymano wiadomość: {user_message}")
        
        reply_text = generate_ai_content(f"Jesteś pomocnym asystentem o imieniu Marcin. Odpowiedz krótko i naturalnie: {user_message}")
        await update.message.reply_text(reply_text)

def main():
    Thread(target=run_health_check_server, daemon=True).start()
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    logger.info("Uruchomiono polling bota...")
    application.run_polling()

if __name__ == "__main__":
    main()
