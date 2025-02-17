Programma di assistente vocale - AI in italiano.

Il programma ha l'obiettivo di fornire supporto vocale principalmente su sistema GNU/Linux (provato con ambiente grafico KDE).
Con il progressivo sviluppo si cercherà renderlo cross-platform. (Alcune sezioni di codice lo sono già.)
E' dotato di animazione grafica che permette di capire quando l'assistente è pronto per ricevere programmi (il nome dell'assistente diventa di color rosso), diversamente stà in attesa di riconoscere la voce di attivazione (nello specifico corrisponde al nome evidenziato sopra l'animazione grafica.)
E' possibile posizionare l'animazione dove di preferisce all'interno dello schermo.
Per chiudere l'appicazione è sufficiente dire "esci dal programma" o premere con il tasto destro del mouse sopra l'animazione.
All'avvio il programma effettua una scansione dei bookmarks contenuti nel browser e dei programmi iinstallati nel sistema operativo.
In qesto modo è possibile aprire e chiudere pagine web o programmi del sistema operativo con i comandi vocali "apri","aprimi" e i relativi di chiusura "chiudi","esci".
Oltre a questo è possibile gestire il controllo del volume di sistema usando i comandi "aumenta il volume", "diminusci il volume","imposta il volume a ..%", oppure "silenzia il volume".
Altra funzione inserita è la possibilità di ascoltare la web radio usando il comando "metti  radio" seguito dal nome della  stazione radio richiesta .
E' possibile verificare quali stazioni radio sono impostate chiedendo la "lista delle stazioni radio"
L'elenco delle webradio può essere modificato agendo sul file stations.csv contenuto nella directory "data".
Ultima funzione disponibile è la possibilità di effettuare una ricerca o un calcolo matematico sfruttando l'IA fornita da Groq .(Per questo serve una API key fornita da Groq da inserire all'interno del file .env (da allocare nella directory "script") con parametro API_KEY = ..... e la chiave fornita da Groq )
L'uso della IA si attiva automaticamente con i comandi "cerca" o "calcola".
Con la versione 2.4 e' stata integrata la possibilità di cercare video su youtube con il comando "cerca.... su Youtube".
Anche in questo caso perchè il comando funzioni  occorre scaricare un API_KEY_YOTUBE da inserire nel file .env.
