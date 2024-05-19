# RemindMe Telegram Bot

RemindMe nasce dall'esigenza di avere promemoria sincronizzati su più dispositivi contemporaneamente, in modo da ricevere le notifiche su tutti i dispositivi in cui è collegato l'account Telegram. È anche possibile scegliere l'opzione di ricevere il promemoria a intervalli di un determinato numero di giorni.

Il bot, una volta avviato il comando **/start**, saluta l'utente e mostra i comandi da utilizzare per l'inserimento, la visualizzazione e la rimozione dei promemoria.

Il comando **/add** permette l'inserimento del promemoria impostando, attraverso i pulsanti, la data e l'orario in cui si desidera ricevere il promemoria.

Il comando **/show** permette all'utente di visualizzare i promemoria impostati precedentemente e permette di eliminarli attraverso l'apposito pulsante.

## Descrizione del Codice
Il codice sviluppa un bot per Telegram che permette agli utenti di aggiungere, visualizzare e rimuovere promemoria. Di seguito è descritta la struttura e il funzionamento delle principali componenti del bot:

#### 1. Importazioni e Configurazioni Iniziali
Il codice inizia con l'importazione delle librerie necessarie, tra cui telegram per la gestione del bot e datetime per la manipolazione delle date. Viene anche configurato il token di accesso e un dizionario per la conversione dei mesi da stringhe a numeri.

#### 2. Funzione start
Questa funzione invia un messaggio di benvenuto all'utente, informandolo dei comandi disponibili per interagire con il bot.

#### 3. Paginazione e Tastiera di Navigazione
Le funzioni **paginate** e **create_pagination_keyboard** suddividono una lista di elementi in pagine e creano una tastiera per la navigazione tra le pagine. Sono utilizzate per gestire l'interazione dell'utente con il calendario per la selezione di data e ora.

#### 4. Callback del Calendario
La funzione **calendar_callback** gestisce le interazioni dell'utente con la tastiera del calendario. Permette all'utente di selezionare giorno, mese, anno, ora, minuto e intervallo per il promemoria.

#### 5. Aggiunta dei Promemoria
La funzione **add** avvia la procedura di aggiunta di un nuovo promemoria, richiedendo all'utente di selezionare il giorno tramite una tastiera interattiva.

#### 6. Gestione del Messaggio di Promemoria
La funzione **handle_reminder_message** gestisce il messaggio del promemoria una volta che l'utente ha inserito tutti i dettagli richiesti. Viene programmato l'invio del promemoria alla data e ora specificate, con eventuale ripetizione in base all'intervallo impostato.

#### 7. Pianificazione e Invio dei Promemoria
Le funzioni **schedule_reminder** e **schedule_next_reminder** pianificano l'invio dei promemoria agli utenti. Utilizzano il job queue di telegram.ext per programmare l'invio dei messaggi all'ora stabilita. La funzione send_reminder invia effettivamente il promemoria all'utente.

#### 8. Visualizzazione e Rimozione dei Promemoria
La funzione **show_reminders** mostra i promemoria salvati per l'utente corrente, mentre **handle_remove_callback** gestisce la rimozione di un promemoria specifico quando l'utente lo richiede.

#### 9. Funzione Principale e Avvio del Bot
La funzione main configura l'applicazione del bot, aggiungendo i gestori per i vari comandi e callback. Utilizza il metodo run_polling per iniziare a ricevere e gestire le richieste degli utenti.
