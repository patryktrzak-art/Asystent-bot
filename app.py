import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import google.generativeai as genai

# Konfiguracja logowania, aby widzieć co się dzieje w konsoli Render.com
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# Konfiguracja klucza API Gemini
genai.configure(api_key='AQ.Ab8RN6KJTHdl-LjfC2YObUmGaTj99wtl78k2AVSQ4FOFO1F-zA')

# Inicjalizacja modelu Gemini (używamy szybkiego i wydajnego modelu flash)
model = genai.GenerativeModel('gemini-1.5-flash')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Obsługa komendy /start"""
  await update.message.reply_text(
      'Cześć! Jestem gotowy do działania. Napisz do mnie cokolwiek!'
  )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """Obsługa każdej wiadomości tekstowej od użytkownika"""
  user_message = update.message.text
  try:
    # Wysyłanie zapytania do Gemini
    response = model.generate_content(user_message)
    # Odesłanie odpowiedzi bota na Telegram
    await update.message.reply_text(response.text)
  except Exception as e:
    logging.error(f'Błąd podczas generowania odpowiedzi: {e}')
    await update.message.reply_text(
        'Przepraszam, wystąpił problem z przetworzeniem Twojej wiadomości.'
    )


def main():
  # Token Twojego bota z Telegrama (najlepiej pobierać go ze zmiennych środowiskowych Render,
  # ale jeśli wolisz, możesz też wpisać go tutaj w cudzysłowie)
  telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', 'TUTAJ_WPISZ_TOKEN_TELEGRAM')

  # Tworzenie aplikacji bota
  app = ApplicationBuilder().token(telegram_token).build()

  # Rejestrowanie handlerów
  app.add_handler(CommandHandler('start', start))
  app.add_handler(
      MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
  )

  print('Bot został uruchomiony i nasłuchuje...')

  # Uruchomienie bota w pętli ciągłej (Polling)
  app.run_polling()


if __name__ == '__main__':
  main()
