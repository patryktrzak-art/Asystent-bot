import logging
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from apscheduler.schedulers.background import BackgroundScheduler
from google import genai
from telegram import Update
from telegram.ext import (
ApplicationBuilder,
ContextTypes,
MessageHandler,
filters,
)
​Konfiguracja logowania
​logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO,
)
logger = logging.getLogger(name)
​--- DANE AUTORYZACJI ---
​TELEGRAM_TOKEN = "WSTAWI_TUTAJ_SWOJ_TOKEN_TELEGRAM"
GEMINI_API_KEY = "WSTAWI_TUTAJ_SWOJ_KLUCZ_GEMINI"
CHAT_ID = 9121741673
​Inicjalizacja klienta Gemini
​client = genai.Client(api_key=GEMINI_API_KEY)
​Prosty serwer WWW dla Rendera (żeby spełnić wymagania portu)
​class HealthCheckHandler(BaseHTTPRequestHandler):
def do_GET(self):
self.send_response(200)
self.end_headers()
self.wfile.write(b"Bot Marcin dziala poprawnie!")
​def run_health_check_server():
port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
logger.info(f"Uruchomiono serwer portu na {port}")
server.serve_forever()
​Funkcja do generowania wiadomości od AI
​def generate_ai_content(prompt: str) -> str:
try:
response = client.models.generate_content(
model="gemini-2.5-flash",
contents=prompt,
)
return response.text
except Exception as e:
logger.error(f"Błąd podczas generowania treści z Gemini: {e}")
try:
response = client.models.generate_content(
model="gemini-flash", contents=prompt
)
return response.text
except Exception as e2:
logger.error(f"Błąd modelu zapasowego: {e2}")
return "Przepraszam, wystąpił problem techniczny z generowaniem treści."
​Automatyczne zadanie: Codzienny raport
​async def send_daily_report(application):
prompt = "Przygotuj krótkie, motywujące powitanie na dzisiejszy poranek oraz podaj jedną ciekawostkę ze świata technologii lub nauki."
text = generate_ai_content(prompt)
try:
await application.bot.send_message(chat_id=CHAT_ID, text=text)
logger.info("Wysłano codzienny raport.")
except Exception as e:
logger.error(f"Błąd wysyłania codziennego raportu: {e}")
​Odpowiedź na wiadomości użytkownika
​async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
if update.message and update.message.text:
user_message = update.message.text
logger.info(f"Otrzymano wiadomość: {user_message}")
​full_prompt = (
f"Jesteś pomocnym asystentem o imieniu Marcin. "
f"Odpowiadaj naturalnie i rzeczowo na poniższą wiadomość użytkownika: {user_message}"
)
​reply_text = generate_ai_content(full_prompt)
await update.message.reply_text(reply_text)
​def main():
# Uruchomienie serwera portu w osobnym wątku dla Rendera
Thread(target=run_health_check_server, daemon=True).start()
​# Inicjalizacja aplikacji Telegram
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(
MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)
​# Harmonogram (APScheduler)
scheduler = BackgroundScheduler(timezone="Europe/Warsaw")
scheduler.add_job(
lambda: application.job_queue.run_once(
lambda ctx: client.loop.create_task(send_daily_report(application)), 0
),
"cron",
hour=8,
minute=0,
)
scheduler.start()
​logger.info("Bot został uruchomiony i działa w tle...")
application.run_polling()
​if name == "main":
main()
