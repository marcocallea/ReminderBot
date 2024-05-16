import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from bot import start, MIOTOKEN
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
