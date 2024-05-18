import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from bot import (
    start,
    create_pagination_keyboard,
    paginate,
    calendar_callback,
    add
)
import bot

class TestStartFunction(unittest.IsolatedAsyncioTestCase):
    async def test_start(self):
        # Mock the Update and Context objects
        update = AsyncMock()
        context = AsyncMock()
        update.effective_user.first_name = "Nome"
        update.effective_user.last_name = "Cognome"

        # Execute the start function
        await start(update, context)

        # Verify that reply_text was called correctly
        update.message.reply_text.assert_awaited_once_with(
            "Ciao Nome Cognome, benvenuto su RemindMe Bot, usa il comando /add per iniziare! Ricorda puoi anche usare il comando /show per mostrare i promemoria già inseriti."
        )

class TestPaginateFunction(unittest.TestCase):
    def test_paginate_first_page(self):
        items = list(range(100))  # Una lista di 100 elementi numerici
        page, has_previous, has_next = paginate(items, page=0, per_page=10)
        self.assertEqual(
            page, list(range(10))
        )  # Conferma che la prima pagina sia corretta
        self.assertFalse(has_previous)  # Non ci dovrebbero essere pagine precedenti
        self.assertTrue(has_next)  # Ci dovrebbero essere pagine successive

    def test_paginate_middle_page(self):
        items = list(range(100))
        page, has_previous, has_next = paginate(items, page=5, per_page=10)
        self.assertEqual(page, list(range(50, 60)))  # Elementi dalla posizione 50 a 59
        self.assertTrue(has_previous)  # Ci dovrebbero essere pagine precedenti
        self.assertTrue(has_next)  # Ci dovrebbero essere pagine successive

    def test_paginate_last_page(self):
        items = list(range(100))
        page, has_previous, has_next = paginate(items, page=9, per_page=10)
        self.assertEqual(page, list(range(90, 100)))  # Ultimi 10 elementi
        self.assertTrue(has_previous)  # Ci dovrebbero essere pagine precedenti
        self.assertFalse(has_next)  # Non ci dovrebbero essere pagine successive

    def test_paginate_empty(self):
        items = []
        page, has_previous, has_next = paginate(items, page=0, per_page=10)
        self.assertEqual(page, [])  # Nessun elemento
        self.assertFalse(has_previous)  # Non ci dovrebbero essere pagine precedenti
        self.assertFalse(has_next)  # Non ci dovrebbero essere pagine successive

class TestPaginationFunctions(unittest.IsolatedAsyncioTestCase):
    def test_create_pagination_keyboard(self):
        prefix = "day"
        items = list(range(1, 32))
        page = 0
        per_page = 7
        keyboard_markup = create_pagination_keyboard(items, page, per_page, prefix)

        self.assertIsInstance(keyboard_markup, InlineKeyboardMarkup)
        self.assertTrue(len(keyboard_markup.inline_keyboard) > 0)

class TestCalendarCallback(unittest.TestCase):
    async def test_day_selection(self):
        # Test the selection of a day
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "day-10"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["day"], 10)
        query.edit_message_text.assert_awaited_once()

    async def test_month_selection(self):
        # Test the selection of a month
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "month-Feb"
        month_to_number = {"Feb": 2}
        context.user_data = {}
        context.bot_data = {"month_to_number": month_to_number}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["month"], 2)
        query.edit_message_text.assert_awaited_once()

    async def test_year_selection(self):
        # Test the selection of a year
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "year-2025"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["year"], 2025)
        query.edit_message_text.assert_awaited_once()

    async def test_hour_selection(self):
        # Test the selection of an hour
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "hour-13"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["hour"], 13)
        query.edit_message_text.assert_awaited_once()

    async def test_minute_selection(self):
        # Test the selection of a minute
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "minute-45"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["minute"], 45)
        query.edit_message_text.assert_awaited_once()

    async def test_interval_selection(self):
        # Test the selection of an interval
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "interval-15"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["interval"], 15)
        query.edit_message_text.assert_awaited_once()

    async def test_final_message_prompt(self):
        # Test the prompt for the final message after selecting the interval
        update = MagicMock()
        context = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "interval-20"
        context.user_data = {}

        await calendar_callback(update, context)

        query.answer.assert_awaited()
        query.edit_message_text.assert_awaited_with(
            "Inserisci il messaggio del promemoria! :"
        )

    @patch("bot.create_pagination_keyboard")
    async def test_add(self, mock_create_pagination_keyboard):
        # Configura il mock per la create_pagination_keyboard
        mock_keyboard = AsyncMock()
        mock_create_pagination_keyboard.return_value = mock_keyboard

        # Esegui la funzione
        await add(self.update, self.context)

        # Verifica che create_pagination_keyboard sia stato chiamato correttamente
        mock_create_pagination_keyboard.assert_called_once_with(
            range(1, 32), 0, 8, "day"
        )

        # Verifica che reply_text sia stato chiamato correttamente
        self.update.message.reply_text.assert_awaited_once_with(
            "Scegli il giorno:", reply_markup=mock_keyboard
        )

class TestMain(unittest.TestCase):
    @patch("bot.ApplicationBuilder")
    def test_main(self, mock_ApplicationBuilder):
        # Setup
        mock_application = MagicMock()
        mock_ApplicationBuilder.return_value.token.return_value.build.return_value = (
            mock_application
        )

        # Esecuzione
        bot.main()

        # Verifica che l'istanza dell'applicazione sia stata creata correttamente
        mock_ApplicationBuilder.assert_called_once()
        mock_ApplicationBuilder.return_value.token.assert_called_once_with(bot.MIOTOKEN)
        mock_ApplicationBuilder.return_value.token.return_value.build.assert_called_once()

        # Verifica che run_polling sia stato chiamato
        mock_application.run_polling.assert_called_once()




if __name__ == "__main__":
    unittest.main()
