from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

MIOTOKEN = ""  # inserite il vostro token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Ciao {update.effective_user.first_name} {update.effective_user.last_name}, benvenuto su RemindMe Bot, usa il comando /add per iniziare! Ricorda puoi anche usare il comando /show per mostrare i promemoria già inseriti."
    )


def main():
    application = ApplicationBuilder().token(MIOTOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
