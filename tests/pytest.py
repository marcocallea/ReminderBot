"""
Unittests di bot.py
"""

from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import InlineKeyboardMarkup
import bot

class TestStartFunction(IsolatedAsyncioTestCase):
    """
    Classe per la funzione start
    """
    async def test_start(self):
        """
        Testa la funzione start
        """
        # Mock the Update and Context objects
        update = AsyncMock()
        context = MagicMock()
        update.effective_user.first_name = "Nome"
        update.effective_user.last_name = "Cognome"

        # Execute the start function
        await bot.start(update,context)

        # Verify that reply_text was called correctly
        update.message.reply_text.assert_awaited_once_with(
            "Ciao Nome Cognome, benvenuto su RemindMe Bot, usa il comando /add per iniziare! "
            "Ricorda puoi anche usare il comando /show per mostrare i promemoria già inseriti."
        )

class TestPaginateFunction(TestCase):
    """
    Classe per la funzione di paginazione
    """
    def test_paginate_first_page(self):
        """
        Test prima pagina
        """
        items = list(range(100))  # A list of 100 numerical elements
        page, has_previous, has_next = bot.paginate(items, page=0, per_page=10)
        self.assertEqual(
            page, list(range(10))
        )  # Confirm that the first page is correct
        self.assertFalse(has_previous)  # There should be no previous pages
        self.assertTrue(has_next)  # There should be next pages

    def test_paginate_middle_page(self):
        """
        Test pagina normale
        """
        items = list(range(100))
        page, has_previous, has_next = bot.paginate(items, page=5, per_page=10)
        self.assertEqual(page, list(range(50, 60)))  # Elements from position 50 to 59
        self.assertTrue(has_previous)  # There should be previous pages
        self.assertTrue(has_next)  # There should be next pages

    def test_paginate_last_page(self):
        """
        Test ultima pagina
        """
        items = list(range(100))
        page, has_previous, has_next = bot.paginate(items, page=9, per_page=10)
        self.assertEqual(page, list(range(90, 100)))  # Last 10 elements
        self.assertTrue(has_previous)  # There should be previous pages
        self.assertFalse(has_next)  # There should be no next pages

    def test_paginate_empty(self):
        """
        Test pagina vuota
        """
        items = []
        page, has_previous, has_next = bot.paginate(items, page=0, per_page=10)
        self.assertEqual(page, [])  # No elements
        self.assertFalse(has_previous)  # There should be no previous pages
        self.assertFalse(has_next)  # There should be no next pages

class TestPaginationFunctions(IsolatedAsyncioTestCase):
    """
    Classe test funzione paginazione
    """
    def test_create_pagination_keyboard(self):
        """
        Test della funzione create_pagination_keyboard
        """
        prefix = "day"
        items = list(range(1, 32))
        page = 0
        per_page = 7
        keyboard_markup = bot.create_pagination_keyboard(items, page, per_page, prefix)

        self.assertIsInstance(keyboard_markup, InlineKeyboardMarkup)
        self.assertTrue(len(keyboard_markup.inline_keyboard) > 0)


class TestCalendarCallback(TestCase):
    """
    Classe per i test della calendarcallback
    """
    async def test_day_selection(self):
        """
        Test selezione giorno
        """
        # Test the selection of a day
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "day-10"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["day"], 10)
        query.edit_message_text.assert_awaited_once()

    async def test_month_selection(self):
        """
        Test selezione mese
        """
        # Test the selection of a month
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "month-Feb"
        month_to_number = {"Feb": 2}
        context = MagicMock()
        context.user_data = {}
        context.bot_data = {"month_to_number": month_to_number}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["month"], 2)
        query.edit_message_text.assert_awaited_once()

    async def test_year_selection(self):
        """
        Test selezione anno
        """
        # Test the selection of a year
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "year-2025"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["year"], 2025)
        query.edit_message_text.assert_awaited_once()

    async def test_hour_selection(self):
        """
        Test selezione ora
        """
        # Test the selection of an hour
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "hour-13"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["hour"], 13)
        query.edit_message_text.assert_awaited_once()

    async def test_minute_selection(self):
        """
        Test selezione minuti
        """
        # Test the selection of a minute
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "minute-45"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["minute"], 45)
        query.edit_message_text.assert_awaited_once()

    async def test_interval_selection(self):
        """
        Test selezione intervallo
        """
        # Test the selection of an interval
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "interval-15"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        self.assertEqual(context.user_data["interval"], 15)
        query.edit_message_text.assert_awaited_once()

    async def test_final_message_prompt(self):
        """
        Test messaggio finale
        """
        # Test the prompt for the final message after selecting the interval
        update = MagicMock()
        query = AsyncMock()
        update.callback_query = query
        query.data = "interval-20"
        context = MagicMock()
        context.user_data = {}

        await bot.calendar_callback(update, context)

        query.answer.assert_awaited()
        query.edit_message_text.assert_awaited_with(
            "Inserisci il messaggio del promemoria! :"
        )

    @patch("bot.create_pagination_keyboard")
    async def test_add(self, mock_create_pagination_keyboard):
        """
        Test funzione add
        """
        # Setup mock for create_pagination_keyboard
        mock_keyboard = AsyncMock()
        mock_create_pagination_keyboard.return_value = mock_keyboard

        # Execute the function
        update = MagicMock()
        await bot.add(update)

        # Verify that create_pagination_keyboard was called correctly
        mock_create_pagination_keyboard.assert_called_once_with(
            range(1, 32), 0, 8, "day"
        )

        # Verify that reply_text was called correctly
        update.message.reply_text.assert_awaited_once_with(
            "Scegli il giorno:", reply_markup=mock_keyboard
        )


class TestMain(TestCase):
    """
    Classe di test della main
    """

    @patch("bot.ApplicationBuilder")
    def test_main(self, mock_application_builder):
        """
        Test del main
        """
        # Setup
        mock_application = MagicMock()
        mock_application_builder.return_value.token.return_value.build.return_value = (
            mock_application
        )

        # Execution
        bot.main()

        # Verify that the application instance was created correctly
        mock_application_builder.assert_called_once()
        mock_application_builder.return_value.token.assert_called_once_with(bot.MIOTOKEN)
        mock_application_builder.return_value.token.return_value.build.assert_called_once()

        # Verify that run_polling was called
        mock_application.run_polling.assert_called_once()
