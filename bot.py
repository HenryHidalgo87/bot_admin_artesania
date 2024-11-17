import logging
import os
import datetime
from dotenv import load_dotenv
from flask import Flask
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Configura el registro para depuración
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token del bot (asegúrate de que esté configurado correctamente)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Lista de palabras inapropiadas
BAD_WORDS = ["idiota", "imbécil", "estúpido", "tonto", "gilipollas", "capullo", 
    "cabron", "cabrona", "mierda", "puta", "puto", "joder", "coño", 
    "maldito", "hostia", "carajo", "pendejo", "maricón", "zorra", 
    "bastardo", "pajero", "cabrón", "polla", "pelotas", "culero", 
    "perra", "gilipollas", "huevón", "mierd*", "cago", "cagarse", 
    "cagada", "chinga", "chingar", "cojones", "cojonudo", "mamón", 
    "pendejada", "pendej*", "putada", "sudaca", "moro", "negrata", 
    "marica", "mariconazo", "mierdoso", "hijodeputa", "culiado", 
    "culiando", "verga", "putear", "chingadera", "imbécil"]

# Preguntas frecuentes y respuestas automáticas
FAQ_RESPONSES = {
    # Preguntas sobre trabajo
    "¿dónde puedo encontrar trabajo?": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "donde encuentro trabajo": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "busco trabajo": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "necesito trabajo": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "¿hay ofertas de trabajo?": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "hay trabajos": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "ofertas de empleo": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "empleo": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "¿dónde hay trabajo?": "Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",
    "Hola quisiera ver ofertas de trabajo en Arona":"Puedes encontrar ofertas laborales en nuestro canal dedicado a <a href='https://t.me/arona_tenerife/4'>empleo</a>.",

    # Preguntas sobre alquiler de pisos
    "¿hay pisos para alquilar?": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "hay pisos en alquiler": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "necesito alquilar un piso": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "busco piso para alquilar": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "¿dónde puedo alquilar un piso?": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "quiero alquilar un piso": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "pisos en alquiler": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "alquiler de pisos": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "alquiler de piso": "Revisa las publicaciones recientes en el canal de <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    "¿hay viviendas para alquilar?": "Revisa las publicaciones recientes en <a href='https://t.me/arona_tenerife/12'>alquileres</a>.",
    

    # Preguntas sobre anunciar productos o servicios
    "¿cómo comparto mi producto o servicio?": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "como anuncio mi producto": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "dónde puedo anunciar un servicio": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "quiero promocionar un producto": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "¿cómo puedo anunciarme?": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "necesito promocionar mi negocio": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "¿cómo promociono mi servicio?": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "¿dónde puedo anunciarme?": "Utiliza la sección de anuncios para promocionar productos y servicios.",
    "¿hay algún lugar para promocionar productos?": "Utiliza la sección de anuncios para promocionar productos y servicios."
}


# Define la función de bienvenida para nuevos miembros
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    for member in update.message.new_chat_members:
        user_name = member.first_name
        welcome_message = (
            f"¡Bienvenid@ {user_name}! a Arona, #Tenerife! 🌞\n\n"
            "Este grupo es un espacio creado para todos los que desean compartir, colaborar y encontrar información útil en nuestra comunidad. Aquí encontrarás varios temas que pueden ayudarte en tu día a día.\n\n"
            "- Ofertas de Trabajo 💼\n"
            "- Alquiler de Pisos 🏠\n"
            "- Nuestras Redes Sociales 🌐\n"
            "- Mi Gurú Carpooling 🚗\n"
            "- Compra y Venta de Coches 🚘\n"
            "- Anúnciate 📢\n"
            "- Compras 🛍️\n"
            "- Ventas 💰\n\n"
            "Esperamos que disfrutes de este espacio y que encuentres lo que buscas. ¡Participa, pregunta y colabora!\n\n"
            "Admin_TNF"
        )
        await update.message.reply_text(welcome_message)

# Función de moderación de lenguaje
async def moderate_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    if any(bad_word in user_message for bad_word in BAD_WORDS):
        await update.message.delete()
        await update.message.reply_text("Tu mensaje ha sido eliminado por contener palabras inapropiadas.")

# Función de antispam para enlaces
async def antispam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    if "http://" in user_message or "https://" in user_message:
        await update.message.delete()
        await update.message.reply_text("Los enlaces no están permitidos en este grupo.")


# Función para respuestas automáticas con formato HTML
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.lower()
    response = FAQ_RESPONSES.get(user_message)
    if response:
        # Enviar la respuesta usando HTML para formatear los enlaces correctamente
        await update.message.reply_text(response, parse_mode="HTML")


# Define la función de inicio (/start) sin formato Markdown
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    welcome_message = (
        f"¡Bienvenid@ {user_name}! a Arona, #Tenerife! 🌞\n\n"
        "Este grupo es un espacio creado para todos los que desean compartir, colaborar y encontrar información útil en nuestra comunidad. Aquí encontrarás varios temas que pueden ayudarte en tu día a día.\n\n"
        "- Ofertas de Trabajo 💼\n"
        "- Alquiler de Pisos 🏠\n"
        "- Nuestras Redes Sociales 🌐\n"
        "- Mi Gurú Carpooling 🚗\n"
        "- Compra y Venta de Coches 🚘\n"
        "- Anúnciate 📢\n"
        "- Compras 🛍️\n"
        "- Ventas 💰\n\n"
        "Esperamos que disfrutes de este espacio y que encuentres lo que buscas. ¡Participa, pregunta y colabora!\n\n"
        "Admin_TNF"
    )
    await update.message.reply_text(welcome_message)

# # Función para manejar mensajes de texto
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user_message = update.message.text

#     # Llama a las funciones de moderación, antispam y auto respuestas
#     await moderate_language(update, context)
#     await antispam(update, context)
#     await auto_reply(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await moderate_language(update, context)
        await antispam(update, context)
        await auto_reply(update, context)
    except Exception as e:
        logger.error(f"Error al manejar mensaje: {e}")


# Función para enviar recordatorios mensuales
async def send_monthly_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="¡Recordatorio mensual! No olvides revisar las nuevas ofertas y oportunidades en el grupo.")

# Comando para activar recordatorios mensuales
async def start_monthly_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Configura el recordatorio para el primer día de cada mes a las 9:00 AM
    first_day_of_month = datetime.datetime.now().replace(day=1, hour=9, minute=0, second=0, microsecond=0)
    context.job_queue.run_monthly(send_monthly_reminder, time=first_day_of_month.time(), day=1, chat_id=update.effective_chat.id)
    await update.message.reply_text("Recordatorios mensuales activados para el primer día de cada mes a las 9:00 AM.")

# --- NUEVO: Configuración del servidor Flask ---
app = Flask('')

@app.route('/')
def home():
    return "Bot activo y funcionando"

def run_server():
    app.run(host='0.0.0.0', port=3000, debug=False)



# --- Modificación de la función principal ---
def main() -> None:
    # Inicia el servidor Flask en un hilo separado
    threading.Thread(target=run_server).start()

    # Configura el bot de Telegram
    application = Application.builder().token(TOKEN).build()
   # Añade los controladores de comandos y mensajes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("monthly_reminders", start_monthly_reminders))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    # Ejecuta el bot
    application.run_polling()

if __name__ == '__main__':
    main()


