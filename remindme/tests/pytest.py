import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from bot import (
    start,
    create_pagination_keyboard,
    paginate,
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
