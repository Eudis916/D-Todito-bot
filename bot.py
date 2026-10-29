import json
import os
from flask import Flask, request
import telebot

TOKEN = '9188595545:AAHCcl_pv2NjSuhOQMMpFuwI_zhFe7khv48'
bot = telebot.TeleBot(TOKEN)

DB_FILE = 'base_datos_mangas.json'
app = Flask(__name__)


def cargar_bd():
  if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r') as f:
      return json.load(f)
  return {}


def guardar_bd(bd):
  with open(DB_FILE, 'w') as f:
    json.dump(bd, f, indent=4)


# Ruta web para que Render mantenga el bot despierto
@app.route('/')
def index():
  return '¡El bot de D Todito Mangas está activo en la nube!'


# Recibir actualizaciones de Telegram mediante Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
  json_string = request.get_data().decode('utf-8')
  update = telebot.types.Update.de_json(json_string)
  bot.process_new_updates([update])
  return '!', 200


# Auto-registro desde el grupo privado
@bot.message_handler(content_types=['document'])
def registrar_pdf_automatico(message):
  if message.caption:
    enlace_tiktok = message.caption.strip()
    if 'tiktok.com' in enlace_tiktok:
      file_id = message.document.file_id
      bd = cargar_bd()
      bd[enlace_tiktok] = file_id
      guardar_bd(bd)
      bot.reply_to(
          message,
          f'✅ ¡PDF registrado con éxito!\nVinculado al video: {enlace_tiktok}',
      )


# Comando start
@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
  bot.send_message(
      message.chat.id,
      '¡Hola! 📖 Pega aquí el enlace del video de TikTok para recibir tu PDF.',
  )


# Entrega de PDF al usuario en privado
@bot.message_handler(
    func=lambda message: message.chat.type == 'private'
    and not message.text.startswith('/')
)
def entregar_pdf_al_usuario(message):
  enlace_usuario = message.text.strip()
  chat_id = message.chat.id
  bd = cargar_bd()

  if enlace_usuario in bd:
    file_id_pdf = bd[enlace_usuario]
    try:
      bot.send_message(
          chat_id, '¡Enlace verificado! Aquí tienes tu capítulo:'
      )
      bot.send_document(
          chat_id, file_id_pdf, caption='¡Disfruta la lectura! 📖'
      )
    except Exception as e:
      bot.send_message(
          chat_id, 'Ocurrió un error al enviar el archivo. Intenta de nuevo.'
      )
  else:
    bot.send_message(
        chat_id,
        '❌ No reconozco ese enlace o el creador aún no ha vinculado el PDF.',
    )


if __name__ == '__main__':
  # Configurar el Webhook automáticamente al encender
  bot.remove_webhook()
  # Nota: Aquí pondrás la URL que te dé Render más adelante
  # bot.set_webhook(url=f"https://TU-APP-EN-RENDER.onrender.com/{TOKEN}")

  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
