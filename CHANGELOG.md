# Changelog

## [2.5.6] -2025-02-26 
- Inserito nella lista dei comandi la possibilità di inviare anche messaggi testuali 
- corretti bug minori su errori 

## [2.5.5] -2025-02-18 
- Corrette le funzioni riavvia e esci che non lavoravano correttamente in uscita dal programma 

## [2.5.4] -2025-02-18
- Compattato il codice per riconoscimento dei comandi (la funzione esegui_com)
- Inserito il riconoscimento sia della lingua italiana che quella inglese 
- audio = recognizer.listen(source,timeout=10) eliminato phrase_time_limit=25 
- inserita nuova funzione adattalingua per errori di riconoscimento in inglese . Es. mito --> mitology

## [2.5.3] -2025-02-17
- Corretto gestione volume. In precedenza silenziando l'audio non era possibile riattivarlo.
- Inserito il comando "imposta il volume a " %

## [2.5.2] -2025-02-07
- Modificato lo schema di attivazione del programma . Adesso può essere eseguito il comando assieme alla wakeword.
- Risolto l'errore nelle finestre qml usando il comando import Qt.labs.settings 1.1. Basta sostituire con import QtCore.
- Aggiunto il comando per il passaggio diretto ad un altra stazione 

## [2.5.1] -2025-02-06
- reso cross-platform il comando volume
- Inserita deepseek come ai
- Risolto il problema sulla finestra notes.qml dove adessl la textarea permette la selezione del testo
- Rimossa Gemini AI in quanto a pagamento 

## [2.5.0] - 2025-01-30
- Risolto problematica confusione linguistica con si e sistema nella funzione comrecon
- Inserito azzeramento variabili riavvia,attivo e uscita nella funzione downtime_control
- inserimento file messages_it.json nella directory config per separare i messagi e i comandi in italiano

## [2.4.5]
- Inserita finestra qml con indicazione del log dei comandi recepiti
- inserita gemini come ai - ancora opzionale

## [2.4.0]
- inserita google api per ricerca su Youtube
- inserito ricerca variabili configurazione da esterno

## [2.3.0]
- Reso più compatto il codice con aggiunta di funzioni all'interno di comrecon
- aggiunto più risposte alla listreplybot e listsaluti
- corretto alcuni programmi che in italiano recepisce in modo diverso es. krita , konsole,kaffeine in apriProgrammi
- miglioramenti nella gestione do apertura e chiusura dei programmi
- inserito controllo volume
- risolto bug su radio che impediva l'esecuzione di varie condizioni (eliminato elif)
