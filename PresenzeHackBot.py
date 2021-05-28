import logging
from os import name

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from datetime import date
import Database as db
import SEGRETI
from dateutil.parser import parse


TOKEN = SEGRETI.TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

idle_state = True

def data_logic(date_in: str, update: Update):
    date = parse(date_in).date()
    students = db.PresenzeDAO.queryDate(date)
    if(students):
        students_list = students[0][0].split(", ")
        names = "\n".join(students_list)
        message = date.strftime('%d-%m-%Y') + "\n" + names
        update.message.reply_text(message)
    else:
        update.message.reply_text('Nessuno studente presente il ' + date.strftime('%d-%m-%Y'))

    global idle_state
    idle_state = True

def idle(update: Update):
    update.message.reply_text('Scrivi /help per una lista di comandi')


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Ciao {user.mention_markdown_v2()}, scrivi /help per una lista di comandi',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    message = """Comandi:
    /data - Visualizza gli studenti presenti per una certa data
    /allstudents - Visualizza i dati di tutti gli studenti
    /presente - Dai disponibilità a seguire in presenza domani
    /assente - Revoca la disponibilità di seguire in presenza domani
    /disponibili - Visualizza gli studenti disponibili a seguire in presenza domani
    /update - Aggiungi la data di oggi e le relative presenze
    """
    update.message.reply_text(message)


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the right message to the user."""
    if(idle_state):
        idle(update)
    else:
        data_logic(date_in=update.message.text, update=update)

def update_command(update: Update, _: CallbackContext) -> None:    
    oggi = date.today().strftime('%Y-%m-%d')
    db.PresenzeDAO.insertDate(oggi)
    update.message.reply_text('Presenze di oggi aggiornate')

def data_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Scrivi la data per la quale vuoi vedere la lista di partecipanti')
    global idle_state
    idle_state = False

def allstudents_command(update: Update, _: CallbackContext) -> None:
    message = "Dati sugli Studenti:\nNome - Ultima Presenza - Disponibilità\n"
    results = db.PresenzeDAO.queryAllStudents()
    for result in results:
        message += "\n" + result[0] + " - " + result[1].strftime('%d-%m-%Y') + " - " + result[2]
    update.message.reply_text(message)

def presente_command(update: Update, _: CallbackContext) -> None:
    db.PresenzeDAO.updateAvailability(availability='Disponibile', name=update.effective_user.full_name)
    update.message.reply_text('Hai dato disponibilità per domani')

def assente_command(update: Update, _: CallbackContext) -> None:
    db.PresenzeDAO.updateAvailability(availability='Non Disponibile', name=update.effective_user.full_name)
    update.message.reply_text('Hai revocato la disponibilità per domani')

def disponibili_command(update: Update, _: CallbackContext) -> None:
    message = "Studenti disponibili:\nNome - Ultima Presenza\n"
    results = db.PresenzeDAO.queryAvailableStudents()
    for result in results:
        message += "\n" + result[0] + " - " + result[1].strftime('%d-%m-%Y')
    update.message.reply_text(message)

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("data", data_command))
    dispatcher.add_handler(CommandHandler("allstudents", allstudents_command))
    dispatcher.add_handler(CommandHandler("presente", presente_command))
    dispatcher.add_handler(CommandHandler("assente", assente_command))
    dispatcher.add_handler(CommandHandler("disponibili", disponibili_command))
    dispatcher.add_handler(CommandHandler("update", update_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()