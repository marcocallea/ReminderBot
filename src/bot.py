import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, CallbackContext
from datetime import datetime, timedelta


MIOTOKEN = ""  # inserite il vostro token
reminders = {}

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

async def handle_reminder_message(
        update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    #parte solo se l'utente ha inserito tutti gli attributi
    if all(
            key in context.user_data
            for key in ["day", "month", "year", "hour", "minute", "interval"]
    ):
        date_str = f"{context.user_data['year']}-{context.user_data['month']}-{context.user_data['day']} {context.user_data['hour']}:{context.user_data['minute']}:00"
        when = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        message = (
            update.message.text
        )
        interval = context.user_data["interval"]

        chat_id = update.message.chat_id
        reminder_id = f"{chat_id}_{len(reminders.get(chat_id, {}))}"
        reminder = {
            "time": when,
            "interval": interval,
            "message": message,
            "chat_id": chat_id,
        }
        if chat_id not in reminders:
            reminders[chat_id] = {}
        reminders[chat_id][reminder_id] = reminder

        # chiamiamo la schedule_reminder per programmare effettivamente l'invio del promemoria
        await schedule_reminder(context, reminder_id, reminder)
        await update.message.reply_text(
            f"Promemoria {message} impostato con il seguente ID: {reminder_id}, Il promemoria verrà inviato ogni {interval} giorni!"
        )

        # Puliamo i dati dell'utente dopo aver aggiunto il promemoria
        del context.user_data["day"]
        del context.user_data["month"]
        del context.user_data["year"]
        del context.user_data["hour"]
        del context.user_data["interval"]


async def schedule_reminder(
        context: ContextTypes.DEFAULT_TYPE, reminder_id: str, reminder: dict
):
    now = datetime.now()

    if reminder["time"] <= now:
        # Se l'ora specificata nel promemoria è già passata, pianifica il primo invio per il minuto successivo
        next_time = now + timedelta(minutes=1)
    else:
        # Altrimenti, pianifica il primo invio all'ora specificata nel promemoria
        next_time = reminder["time"]

    # Calcola il ritardo fino al primo invio
    delay = (next_time - now).total_seconds()
    await schedule_next_reminder(context, reminder_id, reminder, delay)


async def schedule_next_reminder(
        context: ContextTypes.DEFAULT_TYPE, reminder_id: str, reminder: dict, delay: float
):
    def job_callback(context: CallbackContext):
        chat_id = reminder["chat_id"]
        if reminder_id in reminders.get(chat_id, {}):
            asyncio.create_task(
                send_reminder(context.bot, chat_id, reminder["message"], reminder_id)
            )
            if reminder["interval"] != 0:
                # Programma il prossimo promemoria
                context.job_queue.run_once(job_callback, reminder["interval"] * 60)
        else:
            print(
                f"Il promemoria {reminder['message']} è stato rimosso, quindi non verrà inviato nuovamente."
            )
            return

    # Programma il job per il promemoria corrente
    context.job_queue.run_once(job_callback, delay)

async def send_reminder(bot: Bot, chat_id: int, message: str, reminder_id: str):
    # Inviare il messaggio usando l'oggetto bot
    await bot.send_message(chat_id=chat_id, text="\uE142" f" Promemoria: {message}")
    await asyncio.sleep(2)
    if (
            reminder_id in reminders.get(chat_id, {})
            and reminders[chat_id][reminder_id]["interval"] == 0
    ):
        # Rimuovi il promemoria una volta inviato se l'intervallo è 0
        del reminders[chat_id][reminder_id]
        if not reminders[chat_id]:
            del reminders[chat_id]
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
