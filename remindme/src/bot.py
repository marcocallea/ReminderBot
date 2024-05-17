from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

MIOTOKEN = ""  # inserite il vostro token

month_to_number = {
    "Gen": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "Mag": 5,
    "Giu": 6,
    "Lug": 7,
    "Ago": 8,
    "Set": 9,
    "Ott": 10,
    "Nov": 11,
    "Dic": 12,
}

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

async def calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    components = data.split("-")
    action_type = components[
        0
    ]  # Definisce il tipo di azione (day, month, year, hour, minute, interval)

    type_config = {
        "day": {
            "range": range(1, 32),
            "per_page": 8,
            "next_step": "month",
            "converter": int,
        },
        "month": {
            "range": [
                "Gen",
                "Feb",
                "Mar",
                "Apr",
                "Mag",
                "Giu",
                "Lug",
                "Ago",
                "Set",
                "Ott",
                "Nov",
                "Dic",
            ],
            "per_page": 6,
            "next_step": "year",
            "converter": str,
        },
        "year": {
            "range": range(2024, 2031),
            "per_page": 5,
            "next_step": "hour",
            "converter": int,
        },
        "hour": {
            "range": range(24),
            "per_page": 6,
            "next_step": "minute",
            "converter": int,
        },
        "minute": {
            "range": range(60),
            "per_page": 8,
            "next_step": "interval",
            "converter": int,
        },
        "interval": {
            "range": range(30),
            "per_page": 11,
            "next_step": "final_message",
            "converter": int,
        },
    }

    if "succ" in components or "prec" in components:
        page = int(components[-1])
        reply_markup = create_pagination_keyboard(
            type_config[action_type]["range"],
            page,
            type_config[action_type]["per_page"],
            action_type,
        )
        await query.edit_message_text(
            f"Scegli {action_type}:", reply_markup=reply_markup
        )
    else:
        converter = type_config[action_type]["converter"]
        selected_value = converter(components[1])
        context.user_data[action_type] = selected_value
        if action_type == "month":
            str_month = context.user_data["month"]
            if str_month in month_to_number:
                month_number = month_to_number[str_month]
                context.user_data["month"] = str(month_number)
        if action_type == "interval":
            await query.edit_message_text("Inserisci il messaggio del promemoria! :")
        else:
            next_step = type_config[action_type]["next_step"]
            reply_markup = create_pagination_keyboard(
                type_config[next_step]["range"],
                0,
                type_config[next_step]["per_page"],
                next_step,
            )
            await query.edit_message_text(
                f"Scegli {next_step}:", reply_markup=reply_markup
            )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Gestisce l'aggiunta dei promemoria
    reply_markup = create_pagination_keyboard(range(1, 32), 0, 8, "day")
    await update.message.reply_text("Scegli il giorno:", reply_markup=reply_markup)

def main():
    application = ApplicationBuilder().token(MIOTOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add))
    
    # Aggiunge gestori per le callback delle query
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^day-"))
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^month-"))
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^year-"))
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^hour-"))
    application.add_handler(CallbackQueryHandler(calendar_callback, pattern="^minute-"))
    application.add_handler(
        CallbackQueryHandler(calendar_callback, pattern="^interval-")
    )

    application.run_polling()

if __name__ == "__main__":
    main()
