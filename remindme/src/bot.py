from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

MIOTOKEN = ""  # inserite il vostro token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"Ciao {update.effective_user.first_name} {update.effective_user.last_name}, benvenuto su RemindMe Bot, usa il comando /add per iniziare! Ricorda puoi anche usare il comando /show per mostrare i promemoria già inseriti."
    )

def paginate(items, page=0, per_page=9):
    start = page * per_page
    end = start + per_page
    has_next = end < len(items)
    has_prev = start > 0
    return items[start:end], has_prev, has_next
 
def create_pagination_keyboard(items, page, per_page, prefix):
    items_page, has_prev, has_next = paginate(items, page, per_page)
    keyboard = [
        [
            InlineKeyboardButton(item, callback_data=f"{prefix}-{item}")
            for item in items_page
        ]
    ]
 
    # Aggiunta dei pulsanti di navigazione
    navigation_row = []
    if has_prev:
        navigation_row.append(
            InlineKeyboardButton(
                "← Precedente", callback_data=f"{prefix}-prec-{page - 1}"
            )
        )
    if has_next:
        navigation_row.append(
            InlineKeyboardButton(
                "Successivo →", callback_data=f"{prefix}-succ-{page + 1}"
            )
        )
    if navigation_row:
        keyboard.append(navigation_row)
 
    return InlineKeyboardMarkup(keyboard)

def main():
    application = ApplicationBuilder().token(MIOTOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == "__main__":
    main()
