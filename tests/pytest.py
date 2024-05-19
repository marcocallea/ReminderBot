"""
Unittests di bot.py
"""

from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from telegram import InlineKeyboardMarkup, Bot, InlineKeyboardButton
from freezegun import freeze_time
import unittest
import bot
from bot import schedule_reminder, schedule_next_reminder, reminders,send_reminder, add, handle_reminder_message, calendar_callback, show_reminders, handle_remove_callback

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

class TestAddFunction(IsolatedAsyncioTestCase):
    """
    classe per funzioni di test funzione add
    """
    async def asyncSetUp(self):
        self.update = AsyncMock()
        self.context = AsyncMock()

    @patch('bot.create_pagination_keyboard')
    async def test_add(self, mock_create_pagination_keyboard):
        # Configura il mock per la create_pagination_keyboard
        mock_keyboard = AsyncMock()
        mock_create_pagination_keyboard.return_value = mock_keyboard

        # Esegui la funzione
        await add(self.update, self.context)

        # Verifica che create_pagination_keyboard sia stato chiamato correttamente
        mock_create_pagination_keyboard.assert_called_once_with(range(1, 32), 0, 8, "day")

        # Verifica che reply_text sia stato chiamato correttamente
        self.update.message.reply_text.assert_awaited_once_with(
            'Scegli il giorno:', reply_markup=mock_keyboard
        )

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
class TestBotReminderFunctions(IsolatedAsyncioTestCase):
    """
    Classe test reminder
    """
    async def test_handle_reminder_message(self):
        update = AsyncMock()
        context = AsyncMock()
        chat_id = 1234
        update.message.chat_id = chat_id
        update.message.text = "Messaggio di prova"
        context.user_data = {
            'day': '14', 'month': '5', 'year': '2024',
            'hour': '12', 'minute': '30', 'interval': 0
        }

        reminders = {}
        with patch('bot.schedule_reminder', new_callable=AsyncMock) as mock_schedule_reminder:
            with patch('bot.reminders', reminders):
                await handle_reminder_message(update, context)
                self.assertIn(chat_id, reminders)
                mock_schedule_reminder.assert_awaited()
                update.message.reply_text.assert_awaited_with(
                    "Promemoria Messaggio di prova impostato con il seguente ID: 1234_0, Il promemoria verrà inviato ogni 0 giorni!")


class TestScheduleReminder(IsolatedAsyncioTestCase):

    @freeze_time("2024-05-13 12:00:00")
    async def test_reminder_time_passed(self):
        context = AsyncMock()
        reminder_id = 'test123'
        reminder = {'time': datetime.now() - timedelta(hours=1)}

        with patch('bot.schedule_next_reminder', new_callable=AsyncMock) as mocked_schedule_next:
            await schedule_reminder(context, reminder_id, reminder)

            expected_delay = 60  # Since reminder is in the past, should be scheduled 1 minute later
            mocked_schedule_next.assert_called_once_with(context, reminder_id, reminder, expected_delay)

    @freeze_time("2024-05-13 12:00:00")
    async def test_reminder_time_future(self):
        context = AsyncMock()
        reminder_id = 'test456'
        reminder = {'time': datetime.now() + timedelta(hours=1)}

        with patch('bot.schedule_next_reminder', new_callable=AsyncMock) as mocked_schedule_next:
            await schedule_reminder(context, reminder_id, reminder)

            expected_delay = 3600  # 1 hour in seconds
            mocked_schedule_next.assert_called_once_with(context, reminder_id, reminder, expected_delay)


class TestScheduleNextReminder(IsolatedAsyncioTestCase):
    """classe per le funzioni di testing della funzione schedule_next_reminder"""
    async def asyncSetUp(self):
        self.context = MagicMock()
        self.context.job_queue = MagicMock()
        self.context.user_data = {'reminders': {}}
        self.reminder = {
            'chat_id': '123456',
            'message': 'Test Reminder',
            'interval': 10  # Intervallo in minuti
        }
        self.reminder_id = 'reminder123'
        self.context.user_data['reminders'][self.reminder_id] = self.reminder


    async def test_schedule_with_existing_reminder(self):
        # Imposta il dizionario globale reminders
        reminders[self.reminder['chat_id']] = {self.reminder_id: self.reminder}

        # Mock asyncio.create_task per intercettare la sua chiamata
        with patch('asyncio.create_task') as mock_create_task:
            # Esegui la funzione principale
            await schedule_next_reminder(self.context, self.reminder_id, self.reminder, 5)

            # Assicurati che la coda dei job abbia programmato il callback correttamente
            args, kwargs = self.context.job_queue.run_once.call_args
            job_callback = args[0]
            self.assertEqual(args[1], 5)  # Verifica il ritardo impostato per la programmazione del job

            # Esegui manualmente il job callback per testare il flusso interno
            job_callback(self.context)
            mock_create_task.assert_called_once()

class TestBotReminderFunctions(IsolatedAsyncioTestCase):
    """
    Classe test funzione reminder
    """
    async def test_handle_reminder_message(self):
        update = AsyncMock()
        context = AsyncMock()
        chat_id = 1234
        update.message.chat_id = chat_id
        update.message.text = "Messaggio di prova"
        context.user_data = {
            'day': '14', 'month': '5', 'year': '2024',
            'hour': '12', 'minute': '30', 'interval': 0
        }

        reminders = {}
        with patch('bot.schedule_reminder', new_callable=AsyncMock) as mock_schedule_reminder:
            with patch('bot.reminders', reminders):
                await handle_reminder_message(update, context)
                self.assertIn(chat_id, reminders)
                mock_schedule_reminder.assert_awaited()
                update.message.reply_text.assert_awaited_with(
                    "Promemoria Messaggio di prova impostato con il seguente ID: 1234_0, Il promemoria verrà inviato ogni 0 giorni!")

class TestReminderMessageFunction(IsolatedAsyncioTestCase):
    """
    classe per testare funzione gestione messaggio
    """
    async def test_interval_selection_handling(self):
        update = AsyncMock()
        context = AsyncMock()

        # Configurazione del mock context.user_data per restituire 10 quando si accede a 'interval'
        context.user_data.__getitem__.side_effect = lambda key: 10 if key == 'interval' else None

        update.callback_query.data = "interval-10"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        await calendar_callback(update, context)

        # Verifiche
        self.assertEqual(context.user_data['interval'], 10, "L'intervallo recuperato non corrisponde al valore atteso.")
        update.callback_query.edit_message_text.assert_awaited_with(
            'Inserisci il messaggio del promemoria! :'
        )


class TestSendFunction(IsolatedAsyncioTestCase):
    """classe per funzioni di test funzione send"""
    async def test_send_reminder(self):
        reminder_id = 1
        bot = AsyncMock(spec=Bot)
        chat_id = 123456
        message = "Ricordati di chiamare!"
        await send_reminder(bot, chat_id, message,reminder_id)
        bot.send_message.assert_awaited_once_with(chat_id=chat_id, text="\uE142 Promemoria: Ricordati di chiamare!")

    async def test_remove_reminder_with_zero_interval(self):
        reminder_id = '1'
        bot = AsyncMock(spec=Bot)
        chat_id = 123456
        message = "Ricordati di chiamare!"

        # Setting up the reminders dictionary with interval 0
        reminders[chat_id] = {
            reminder_id: {
                'message': message,
                'interval': 0
            }
        }

        await send_reminder(bot, chat_id, message, reminder_id)

        # Verify the reminder has been removed
        self.assertNotIn(reminder_id, reminders.get(chat_id, {}),
                         "The reminder was not removed even though the interval was 0.")

        # Optionally, ensure that the chat_id dictionary is also deleted if there are no more reminders
        self.assertNotIn(chat_id, reminders,
                         "The chat_id dictionary was not removed even though there are no more reminders.")


class TestShowRemindersFunction(unittest.IsolatedAsyncioTestCase):
    async def test_show_reminders_empty(self):
        update = AsyncMock()
        context = AsyncMock()
        chat_id = 123456
        update.effective_chat.id = chat_id
        reminders = {}
        # Patch del dizionario dei promemoria
        with patch("bot.reminders", reminders):
            await show_reminders(update, context)
            # Qui, aspettati che la funzione di risposta sia stata chiamata con il messaggio dei promemoria esistenti
            update.message.reply_text.assert_awaited_with("Nessun promemoria salvato!")

    async def test_show_reminders_data(self):
        update = AsyncMock()
        context = AsyncMock()
        chat_id = 123456
        update.message.chat_id = chat_id

        reminders = {
            chat_id: {
                1: {"message": "Visita medica", "time": "2024-05-14", "interval": 30}
            }
        }
        expected_message = "Promemoria: Visita medica,\ncon ID: 1\nimpostato per giorno: 2024-05-14\nsi ripeterà ogni 30 giorni\n"
        expected_keyboard = [
            [InlineKeyboardButton("Rimuovi 1", callback_data="remove-1")]
        ]
        expected_reply_markup = InlineKeyboardMarkup(expected_keyboard)

        with patch("bot.reminders", reminders):
            await show_reminders(update, context)
            update.message.reply_text.assert_awaited_with(
                expected_message, reply_markup=expected_reply_markup
            )


class TesoveFunction(unittest.IsolatedAsyncioTestCase):
    async def test_handle_remove_callback(self):
        # Setup dell'ambiente di test
        chat_id = 123456
        reminder_id = "1"
        reminders = {
            chat_id: {
                reminder_id: {
                    "message": "Visita medica",
                    "time": "2024-05-14",
                    "interval": 30,
                }
            }
        }

        # Creazione di oggetti mock per update e context
        update = AsyncMock()
        update.callback_query = AsyncMock()
        update.callback_query.message = AsyncMock()
        update.callback_query.message.chat_id = chat_id
        update.callback_query.data = f"remove-{reminder_id}"

        # Patching del dizionario reminders all'interno del modulo bot
        with patch("bot.reminders", reminders):
            # Chiamata alla funzione da testare
            await handle_remove_callback(update, update.callback_query)

            # Verifiche
            if chat_id in reminders and reminder_id in reminders[chat_id]:
                self.fail("Il promemoria non è stato rimosso correttamente.")
            elif chat_id not in reminders:
                # Se la chat_id non è più presente, verificare che l'eliminazione sia corretta
                self.assertEqual(
                    len(reminders.get(chat_id, {})),
                    0,
                    "La chat_id è stata rimossa completamente, ma non era vuota.",
                )
            else:
                # Chat esiste ma non ci sono promemoria
                self.assertEqual(
                    len(reminders[chat_id]),
                    0,
                    "Ci sono ancora promemoria quando non dovrebbero essercene.",
                )

            update.callback_query.edit_message_text.assert_awaited_with(
                "Promemoria rimosso con successo!"
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
