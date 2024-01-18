import os
from typing import Final
import requests
from requests.exceptions import RequestException
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Retrieve token and bot username from environment variables
TOKEN: Final = os.getenv('TOKEN', 'default_token')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME', 'default_bot_username')

API_BASE_URL =  os.getenv('API_BASE_URL', 'default_bot_username')

# States for the conversation
AUTH_STATES = range(1)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao, benvenuto su eVDR. In questa chat potrai scoprire l'indizio della settimana e provare a risolverlo con il mio aiuto. Prima di tutto è necessario autenticare la chat. Se sei un Corsaro Nero ti basterà cliccare su questo comando /autenticazione e seguire le istruzioni. Una vola autenticato potrai richiedere l'indizio della settimana utilizzando il comando /indizio. Per sapere come usare il VDR clicca su questo comando /help.\n\nAndiamo a vincere!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao, sono qui per valutare i tuoi ragionamenti, se mi invii una soluzione ti evidenzierò in grassetto le frasi che sono corrette. Per richiedere un VDR è semplicissimo, ti basterà scrivere un messaggio che comincia con \"Proposta soluzione:\", ecco un esempio:\n\nProposta soluzione:\n\nL'indizio della settimana ha una soluzione e questa soluzione porta a Crapolla.")

async def indizio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id: int = update.message.chat.id  # Extract chat ID

    try:
        # Include chat_id in the request to the backend server
        response = requests.post(f"{API_BASE_URL}/bot/indizio", json={"chat_id": chat_id})

        if response.status_code == 200:
            indizio_url = response.json().get("url")
            await update.message.reply_text(indizio_url)
        elif response.status_code == 401:
            await update.message.reply_text("La chat non è stata ancora autenticata. Se sei un Corsaro Nero ti basterà cliccare su questo comando /autenticazione e seguire le istruzioni.")
        else:
            await update.message.reply_text("Spiacente, c'è stato un problema nella connessione al server. Riprova più tardi e magari scrivilo nel gruppo SPAM")
    except RequestException as e:
        # Log the exception here if you have logging set up
        print(f"An error occurred: {e}")
        await update.message.reply_text("Spiacente, c'è stato un problema nella connessione al server. Riprova più tardi e magari scrivilo nel gruppo SPAM")


async def auth_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Scrivi il tuo numero di cellulare per autenticare questa chat.")
    return AUTH_STATES

async def auth_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_number = update.message.text
    chat_id = update.effective_chat.id

    try:
        # Send data to your backend for authentication
        response = requests.post(f"{API_BASE_URL}/bot/auth", json={"phone_number": phone_number, "chat_id": chat_id})
        
        if response.status_code == 200:
            auth_success = response.json().get("success", False)
            if auth_success:
                await update.message.reply_text("Autenticazione avvenuta con successo")
            else:
                await update.message.reply_text("Purtroppo non abbiamo trovato il tuo numero tra i contatti abilitati. Contatta il Capitano per risolvere il problema")
        else:
            await update.message.reply_text("Purtroppo c'è stato un errore nell'elaborare la richiesta, chiedi assistenza al Capitano per risolvere il problema.")
    except RequestException as e:
        # Log the exception here if you have logging set up
        print(f"An error occurred: {e}")
        await update.message.reply_text("Purtroppo c'è stato un errore nell'elaborare la richiesta, chiedi assistenza al Capitano per risolvere il problema.")

    return ConversationHandler.END

# Messages

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    chat_id: int = update.message.chat.id  # Extract chat ID
    text: str = update.message.text

    try:
        # Send message text to backend and get response
        response = requests.post(f"{API_BASE_URL}/bot/conversation", json={"message": text, "message_type": message_type, "chat_id": chat_id})
        
        if response.status_code == 200:
            reply_text = response.json().get("reply")
            await update.message.reply_text(reply_text)
        elif response.status_code == 401:
            await update.message.reply_text("La chat non è stata ancora autenticata. Se sei un Corsaro Nero ti basterà cliccare su questo comando /autenticazione e seguire le istruzioni.")
        else:
            await update.message.reply_text("Spiacente, c'è stato un problema nella connessione al server. Riprova più tardi e magari scrivilo nel gruppo SPAM")
    except RequestException as e:
        # Log the exception here if you have logging set up
        print(f"An error occurred: {e}")
        await update.message.reply_text("Spiacente, c'è stato un problema nella connessione al server. Riprova più tardi e magari scrivilo nel gruppo SPAM.")



# Error handling
    
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Update {update} caused error {context.error}")



if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('indizio', indizio_command))

    # Add ConversationHandler for phone number collection
    auth_handler = ConversationHandler(
        entry_points=[CommandHandler('autenticazione', auth_start)],
        states={
            AUTH_STATES: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth_end)],
        },
        fallbacks=[]
    )

    app.add_handler(auth_handler)

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polling
    print("Polling...")
    app.run_polling(poll_interval=3)