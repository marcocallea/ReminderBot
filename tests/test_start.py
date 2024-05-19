import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
import bot


class TestStartFunction(IsolatedAsyncioTestCase):
    """Classe per la funzione start"""
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




