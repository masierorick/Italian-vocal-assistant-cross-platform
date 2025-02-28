#Assistente vocale con python in italiano
#2025 - Masiero Riccardo - tecnomas.engineering@gmail.com

#Librerie python necessarie per il funzionamento

#pip install gtts
#pip install playsound
#sudo apt install portaudio19-dev
#pip install speechrecognition
#pip install pyproject.toml
#pip install PyAudio
#pip install python-dotenv
#pip install google-api-python-client

#gruppi AI da installare
#pip install groq
#pip install google-generativeai
#On UNIX, run the command below in the terminal
#export GROQ_API_KEY=real api key

import os
import re
import time
import random
import shutil
import signal
import json
import csv
import sys
import platform
import webbrowser
import threading
from threading import Thread
import subprocess
from multiprocessing import Process
from pathlib import Path
from gtts import gTTS
from playsound import playsound
from dotenv import load_dotenv
import speech_recognition as sr
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject,Slot,Signal
#AI importate
from groq import Groq
from openai import OpenAI
from googleapiclient.discovery import build #serve per youtube api

load_dotenv()


#Percorsi principali
main_path = Path.cwd()
current_dir = os.path.dirname(os.path.abspath(__file__))
radios_csv = main_path / "data/stations.csv"
config_path = main_path / "config/config.json"
messages_path = main_path / "config/messages_it.json"

# Carica configurazione da file json
with open(config_path, "r") as config_file:
    config = json.load(config_file)

# Carica i messaggi dal file JSON
with open(messages_path, "r", encoding="utf-8") as f:
    messages = json.load(f)

#variabili globali di configurazione da cercare esternamente nel file config.json
botname = config["botname"]
wakeword = config["wakeword"]
sleep_time = config["sleep_time"]#  secondi per inattività
deltavolume = config["deltavolume"] #valore percentuale


attivo = False
uscita = False
riavvia = False
time_start = 0
parla_sintesi = False # Flag per controllare lo stato della sintesi vocale
numnote= 0
youtubeopen = False
messaggio = ""


#Sequenze di risposta
# Assegna i messaggi alle variabili
listreplybot = messages["welcome_messages"]
listsaluti = messages["goodbye_messages"]
error_file_not_found = messages["error_messages"]["file_not_found"]
radio_list_message = messages["other_messages"]["radio_list"]


#Riconoscimento vocale parametri iniziali
recognizer = sr.Recognizer()
#sensibilità microfono fissa (es. 300) o dinamica
recognizer.energy_threshold = 180
#recognizer.dynamic_energy_threshold = 'False'
recognizer.pause_threshold = 1.2


# Imposta la variabile di ambiente QT_QPA_PLATFORM
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Configura la chiave API e il servizio
api_key_youtube = os.getenv("API_KEY_YOUTUBE") #legge api key di youtube dal file .env
youtube = build("youtube", "v3", developerKey=api_key_youtube)

#Groq API
clientGroq = Groq(api_key=os.getenv("API_KEY"))

#Deepseek API
clientDeepseek = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("APY_KEY_DEEPSEEK")
)

def get_deepseek_response(text):
  italian_prompt = f"Rispondi in italiano.\nTesto dell'utente: {text}"
  response = clientDeepseek.chat.completions.create(
     model="deepseek/deepseek-r1:free",
     messages=[{"role": "user","content": italian_prompt}]
  )
  if response and hasattr(response, "choices") and response.choices:
        return response.choices[0].message.content
  return "Errore nella risposta dell'API."


def get_groq_response(text):
    """Funzione per ottenere risposta da Groq AI."""
    italian_prompt = f"Rispondi in italiano.\nTesto dell'utente: {text}"
    response = clientGroq.chat.completions.create(
        model="Llama3-8b-8192",
        messages=[{"role": "user", "content": italian_prompt}]
    )
    return response.choices[0].message.content



def cerca_youtube(query, max_risultati=5):
    # Cerca video su YouTube
    richiesta = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_risultati
    )
    risposta = richiesta.execute()

    # Mostra i risultati
    urls = []

    for item in risposta["items"]:
        titolo = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        urls.append(url)  # Aggiungi ogni URL alla lista
        print(f"Titolo: {titolo}")
        print(f"URL: {url}")
        print("-" * 40)
    return urls


def speak(text):
    #Sintesi vocale del testo fornito.
    global parla_sintesi

    parla_sintesi = True # Imposta il flag per bloccare il riconoscimento
    tts = gTTS(text=text, lang='it')
    tts.save("response.mp3")
    playsound("response.mp3")
    os.remove("response.mp3")
    parla_sintesi = False  # Libera il flag per consentire il riconoscimento



def downtime_control():
   #Controlla l'inattività dell'assistente.
   global attivo,time_start,sleep_time

   if attivo and time.perf_counter() - time_start >= sleep_time:

        attivo = False
        #ripristino di tutte le variabili alla condizone iniziale
        attivo = False
        uscita = False
        riavvia = False
        scrivistatus()
        print(f"{botname} in stand-by.")



def lista_radio_csv():
   """Stampa e visualizza la lista delle stazioni radio salvate."""
   try:
        with open(radios_csv, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            testo = radio_list_message + "\n"
            for line_count, row in enumerate(reader):
                if line_count > 0:
                    testo += f"{row[0]}\n"

            #avvia la finestra delle note in un processo
            Process(target=notes, args=(testo,), daemon=True).start()

   except FileNotFoundError:
        print(messages["error_messages"]["error_file_not_found"])



def ricerca_stazione_csv(comando):
    """Ricerca una stazione radio e la avvia."""
    try:
        with open(radios_csv, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for line_count, row in enumerate(reader):
                if line_count > 0 and row[0].lower() in comando.lower():
                    play_radio_csv(row[0], row[1])
                    speak("Apro la radio.")
                    return
    except FileNotFoundError:
       print(messages["error_messages"]["error_file_not_found"])


def play_radio_csv(stazione,url):
    """Avvia una stazione radio."""
    if not shutil.which("ffplay"):
        speak("Installa ffmpeg per riprodurre la radio.")
        return
    print(messages["other_messages"]["radio_run"].format(stazione=stazione))
    #os.system(f"ffplay -nodisp -loglevel panic {url} &")
    #modifica per eseguire in un thread la radio e alleggerire il programma
    def start_radio():
        subprocess.Popen(["ffplay", "-nodisp", "-loglevel", "panic", url],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    Thread(target=start_radio, daemon=True).start()



def apriBookmarks(listabookmarks, comando):
    global youtubeopen

    if "youtube" in comando:
        youtubeopen = True
    try:
        with open(listabookmarks, "r") as file:
            for line in file:
                # Rimuovi spazi e linee vuote
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Dividi la riga in chiave e valore
                if "=" in line:
                    bookmark, url = line.split("=", 1)
                    if bookmark.lower() in comando.lower():
                        # Esegui apertura browser all'url trovato
                        #webbrowser.open(url, new=2)
                        # uso thread per evitare overhead e velocizzare l'esecuzione senza complicazioni.
                        Thread(target=webbrowser.open, args=(url, 2), daemon=True).start()
                        speak("Pagina di " + bookmark.lower() + " aperta")
                        return True  # Azione completata, esci dalla funzione
    except FileNotFoundError:
        pass
    return False



def apri_gestore_file(percorso="."):
    # Apre il gestore file predefinito - già reso cross-platform

    try:
        if sys.platform.startswith("win"):  # Windows
            os.startfile(os.path.abspath(percorso))
        elif sys.platform.startswith("darwin"):  # macOS
            subprocess.run(["open", percorso], check=True)
        elif sys.platform.startswith("linux"):  # Linux e varianti
            # Prova diversi file manager popolari
            file_managers = ["xdg-open", "nautilus", "dolphin", "thunar", "pcmanfm"]
            for fm in file_managers:
                if os.system(f"which {fm} > /dev/null 2>&1") == 0:
                    #comando originale
                    #os.system(f"{fm} {percorso}")
                    #comando alternativo
                    subprocess.run([fm, percorso], check=True)
                    break
            else:
                raise RuntimeError("Nessun gestore file trovato.")
        else:
            raise RuntimeError(f"Piattaforma {sys.platform} non supportata.")
    except Exception as e:
        print(messages["error_messages"]["filemanger_error"])



def adattalingua(comando):

  # Modifica comandi recepiti con nomi diversi in italiano
    correzioni = {
        r"\bmito\b": "mitology",
        r"\bmitolo\b": "mitology",
        r"\bcrita\b": "krita",
        r"\bcreta\b": "krita",
        r"\bconsole\b": "konsole",
        r"\bcaffeine\b": "kaffeine",
        r"\bcate\b": "kate"

    }

    for errato, corretto in correzioni.items():
        comando = comando.replace(errato, corretto)
    return comando


def apriProgrammi(listaprogrammi, comando):
    comandomod = adattalingua(comando)  # Funzione per adattare la lingua
    comando = comandomod

    # Caso speciale: apri il browser
    if "browser" in comando:
        # uso thread per evitare overhead e velocizzare l'esecuzione senza complicazioni.
        Thread(target=webbrowser.open, args=('www.google.it', 2), daemon=True).start()
        speak(messages["other_messages"]["browser_opened"])
        return True

    # Caso speciale: apri un'app musicale
    if "musica" in comando:

        musicprog = "clementine"
        try:
            speak(messages["other_messages"]["music_player_opened"].format(musicprog=musicprog))
            os.system(musicprog+"&")  # Sostituisce os.system
            return True
        except FileNotFoundError:
            speak(messages["error_messages"]["program_not_found"])
            return False
        except subprocess.CalledProcessError as e:
            speak(messages["error_messages"]["called_process_error"])
            return False

    # Apri programmi da un file
    try:
        with open(listaprogrammi, "r") as file:
            for line in file:
                # Rimuovi spazi e linee vuote
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Dividi la riga in chiave e valore
                if "=" in line:
                    programma, comando_exe = line.split("=", 1)
                    if programma.lower() in comando.lower():
                        try:
                            # Esegui il programma usando subprocess.Popen
                            subprocess.Popen(comando_exe.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            speak(messages["other_messages"]["program_opened"].format(programma=programma))
                            return True
                        except FileNotFoundError:
                            speak(messages["error_messages"]["program_not_found"])
                            return False
                        except subprocess.CalledProcessError as e:
                            speak(messages["error_messages"]["called_process_error"])


                            return False
    except FileNotFoundError:
        speak(messages["error_messages"]["file_not_found"])
        return False




def chiudiProgrammi(listaprogrammi, comando):

    global youtubeopen

    trovato = False

    if "browser" in comando:
              youtubeopen = False
              os.system("pkill vivaldi-bin")
              speak(messages["other_messages"]["browser_closed"])
              return True
    if "musica" in comando:
              os.system("pkill clementine")
              speak(messages["other_messages"]["music_player_closed"])
              return True

    comandomod=adattalingua(comando)
    comando = comandomod


    try:
         with open(listaprogrammi, "r") as file:
            for line in file:
                # Rimuovi spazi e linee vuote
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Dividi la riga in chiave e valore
                if "=" in line:
                    programma, comando_exe = line.split("=", 1)
                    if programma.lower() in comando.lower():
                        # Esegui il comando dal sistema
                        comando = comando_exe
                        trovato = True

    except FileNotFoundError:
         speak(messages["error_messages"]["file_not_found"])
         return True

    if trovato:
      os.system("pkill " + comando)
      speak(messages["other_messages"]["program_closed"].format(programma=comando))



def scrivistatus(): # Funzione per deternimare lo stato attivo dell'assistente vocale
  global attvo
  with open(current_dir + "/status.py", 'w') as f:
       f.write(f"{"attivo"} = {attivo}\n")



def estraipid(pid1,pid2):

  pattern = r'(\w+)\s*=\s*(.*)'  #\w+ corrisponde alla variabile, .* al valore dopo '='
  with open(current_dir+"/pid.py", 'r') as file:
    for numero_riga, riga in enumerate(file, 1):
       match = re.match(pattern, riga.strip())  # Cerca la corrispondenza
       if match:
            variabile = match.group(1)  # Variabile (prima del '=')
            if ("pid1") in variabile:
              pid1 = int(match.group(2))  # Valore (dopo '=')
              #print (variabile, pid1)
            if ("pid2") in variabile:
              pid2 = int(match.group(2))  # Valore (dopo '=')
              #print (variabile, pid2)


def setVolume(azione):
   #inserita funzione cross-platform
    global deltavolume

    if platform.system() == "Windows":
     try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
     except ImportError:
        print(messages["error_messages"]["program_not_found"].format(program="pycaw"))

    system_platform = platform.system()

    def extract_percentage(azione):
        digits = ''.join(filter(str.isdigit, azione))
        return int(digits) if digits else None

    if system_platform == "Linux":
        percent = extract_percentage(azione)
        if any(word in azione for word in messages["commands"]["setvol"]):
            if percent is not None:
                os.system("pactl set-sink-mute @DEFAULT_SINK@ 0")  # Unmute
                os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {percent}%")
                print(f"Volume impostato a {percent}%")
        elif any(word in azione for word in messages["commands"]["upvol"]):
            os.system("pactl set-sink-mute @DEFAULT_SINK@ 0")  # Unmute
            os.system(f"pactl set-sink-volume @DEFAULT_SINK@ +{deltavolume}%")
            print(messages["other_messages"]["volume_increased"].format(deltavolume=deltavolume))
        elif any(word in azione for word in messages["commands"]["downvol"]):
            os.system("pactl set-sink-mute @DEFAULT_SINK@ 0")  # Unmute
            os.system(f"pactl set-sink-volume @DEFAULT_SINK@ -{deltavolume}%")
            print(messages["other_messages"]["volume_decreased"].format(deltavolume=deltavolume))
        elif any(word in azione for word in messages["commands"]["silent"]):
            os.system("pactl set-sink-mute @DEFAULT_SINK@ toggle")
            print(messages["other_messages"]["volume_muted"])
        else:
            print(messages["error_messages"]["command_not_recognized"])

    elif system_platform == "Darwin":  # macOS
        percent = extract_percentage(azione)
        if any(word in azione for word in messages["commands"]["setvol"]):
            if percent is not None:
                os.system("osascript -e 'set volume output muted false'")  # Unmute
                os.system(f"osascript -e 'set volume output volume {percent}'")
                print(f"Volume impostato a {percent}%")
        elif any(word in azione for word in messages["commands"]["upvol"]):
            os.system("osascript -e 'set volume output muted false'")  # Unmute
            os.system(f"osascript -e 'set volume output volume (output volume of (get volume settings) + {deltavolume})'")
            print(messages["other_messages"]["volume_increased"].format(deltavolume=deltavolume))
        elif any(word in azione for word in messages["commands"]["downvol"]):
            os.system("osascript -e 'set volume output muted false'")  # Unmute
            os.system(f"osascript -e 'set volume output volume (output volume of (get volume settings) - {deltavolume})'")
            print(messages["other_messages"]["volume_decreased"].format(deltavolume=deltavolume))
        elif any(word in azione for word in messages["commands"]["silent"]):
            os.system("osascript -e 'set volume output muted not (output muted of (get volume settings))'")
            print(messages["other_messages"]["volume_muted"])
        else:
            print(messages["error_messages"]["command_not_recognized"])

    elif system_platform == "Windows":
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            percent = extract_percentage(azione)
            if any(word in azione for word in messages["commands"]["setvol"]):
                if percent is not None:
                    volume.SetMute(0, None)  # Unmute
                    volume.SetMasterVolumeLevelScalar(percent / 100, None)
                    print(f"Volume impostato a {percent}%")
            elif any(word in azione for word in messages["commands"]["upvol"]):
                volume.SetMute(0, None)  # Unmute
                volume.SetMasterVolumeLevelScalar(min(volume.GetMasterVolumeLevelScalar() + deltavolume / 100, 1.0), None)
                print(messages["other_messages"]["volume_increased"].format(deltavolume=deltavolume))
            elif any(word in azione for word in messages["commands"]["downvol"]):
                volume.SetMute(0, None)  # Unmute
                volume.SetMasterVolumeLevelScalar(max(volume.GetMasterVolumeLevelScalar() - deltavolume / 100, 0.0), None)
                print(messages["other_messages"]["volume_decreased"].format(deltavolume=deltavolume))
            elif any(word in azione for word in messages["commands"]["silent"]):
                volume.SetMute(not volume.GetMute(), None)
                print(messages["other_messages"]["volume_muted"])
            else:
                print(messages["error_messages"]["command_not_recognized"])
        except Exception as e:
            print(messages["error_messages"]["error_volume_control"].format(system=system_platform))
    else:
        print(messages["error_messages"]["error_system"])



class ProcessManager(QObject):

    def __init__(self, app_window):
        super().__init__()
        self.app_window = app_window

    @Slot()
    def close_window(self):
        """ Chiude la finestra associata """
        if self.app_window:
            self.app_window.close()

    @Slot(str)
    def check_text(self, testo):
        """ Controlla e aggiorna il testo nell'interfaccia QML """

        if self.app_window:
            text_obj = self.app_window.findChild(QObject, "testo")
            if text_obj:
                text_obj.setProperty("text", testo)
            else:
                print("Errore: oggetto 'testo' non trovato in QML.")
        else:
            print("Errore: finestra principale non definita.")





def notes(testo):
    """ Avvia l'applicazione QML e imposta il testo iniziale """
    global numnote  # Mantiene il conteggio delle note

    app = QGuiApplication(sys.argv)

    # Crea l'applicazione
    app.setOrganizationName("TecnoMas")
    app.setOrganizationDomain("tecnomas.engineering.com")
    app.setApplicationName("notes")

    # Configura il file QML e lo carica
    engine = QQmlApplicationEngine()
    engine.load(main_path / 'ui/notes.qml')

    if not engine.rootObjects():
        print(messages["error_messages"]["error_load_qml"])
        sys.exit(-1)

    root_object = engine.rootObjects()[0]

    # Crea l'istanza di ProcessManager e passa la finestra principale
    process_manager = ProcessManager(app_window=root_object)
    engine.rootContext().setContextProperty("processManager", process_manager)  # Collegamento alla classe in QML

    # Aggiorna il testo tramite il metodo check_text
    process_manager.check_text(testo)

    numnote += 1  # Incrementa il conteggio delle note

    # Salva il PID in un file
    with open(current_dir + "/notepid.py", 'w') as f:
        f.write(f"note{numnote} = {os.getpid()}\n")

    app.exec()



def comrecon(comando):

    global attivo, listreplybot, listsaluti, main_path, radios_json, time_start, uscita, riavvia,youtubeopen,messaggio,parla_sintesi
    attendi_conferma = True
    listaprogrammi = main_path / "data/listaprogrammi"
    listabookmarks = main_path / "data/bookmarks"
    pid1, pid2 = 0, 0
    risposte_comando = messages["commands"]["reply"]

    # Normalizzazione del comando
    comando = comando.lower().strip()


    # Scrive lo stato dell'assistente
    scrivistatus()
    time_start = time.perf_counter()

    def rispondi_e_parla(messaggio):
        print(botname + ": " + messaggio)
        speak(messaggio)


    def conferma_uscita():
         global uscita

         if any(re.search(pattern,comando,re.IGNORECASE) for pattern in risposte_comando):
            rispondi_e_parla(messages["other_messages"]["shutdown_executed"])
            os.system("shutdown -h now")
         elif "no" in comando:
            uscita = False
            rispondi_e_parla(messages["other_messages"]["shutdown_cancelled"])

    def conferma_riavvio():
         global riavvia


         if any(re.search(pattern,comando,re.IGNORECASE) for pattern in risposte_comando):
            rispondi_e_parla(messages["other_messages"]["reboot_executed"])
            os.system("sudo reboot")
         elif "no" in comando:
            rispondi_e_parla(messages["other_messages"]["reboot_cancelled"])
            riavvia = False


    def esegui_com(comando):
       global uscita,riavvia

       # Funzione per determinare ed eseguire il comando ricevuto con comandi semplificati
       comandomod = adattalingua(comando)  # Funzione per adattare la lingua
       comando = comandomod

       if not parla_sintesi:
          print(messages["other_messages"]["command"].format(comando=comando))  # Log del comando

       #da tenere le funzioni riavvia e uscita in questo punto
       if riavvia:
           conferma_riavvio()
       if uscita:
             conferma_uscita()

       if any(word in comando for word in messages["commands"]["exit"] + ["chiuditi"]) and any(word in comando for word in messages["objects"]["program"]):
          rispondi_e_parla(random.choice(listsaluti))
          estraipid(pid1, pid2)
          os.kill(pid1, signal.SIGTERM)
          exit()

       if any(word in comando for word in messages["commands"]["restart"]) and any(word in comando  for word in messages["objects"]["pc"]):
            rispondi_e_parla(messages["other_messages"]["command_confirmation"]) #Sei sicuro?
            riavvia = True


       if any(word in comando for word in messages["commands"]["turnoff"]) and any(word in comando for word in messages["objects"]["pc"]):
           rispondi_e_parla(messages["other_messages"]["command_confirmation"]) #Sei sicuro?
           uscita = True


       if any(word in comando for word in messages["commands"]["open"]):
          if "gestore" in comando and "file" in comando:
            apri_gestore_file(".")
          elif not apriBookmarks(listabookmarks, comando):
            apriProgrammi(listaprogrammi, comando)

       if any(word in comando for word in messages["commands"]["close"]):
          if any(word in comando for word in messages["objects"]["window"]):
            rispondi_e_parla(messages["other_messages"]["notes_closed"])
          else:
            chiudiProgrammi(listaprogrammi, comando)

       if "radio" in comando:
          if any(word in comando for word in messages["objects"]["list"]):
            rispondi_e_parla(messages["other_messages"]["radio_list"])
            lista_radio_csv()
          elif any(word in comando for word in messages["objects"]["graphic"]):
            rispondi_e_parla("Apro la radio con PyRadio")
            subprocess.Popen(["pyradio"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
          elif any(word in comando for word in messages["commands"]["change"] + messages["commands"]["open"]):
            os.system("pkill ffplay")
            ricerca_stazione_csv(comando)
          elif any(word in comando for word in messages["commands"]["turnoff"]):
            rispondi_e_parla(messages["other_messages"]["radio_closed"])
            os.system("pkill ffplay")
          elif any(word in comando for word in messages["commands"]["silent"]):
              setVolume(comando)

       if "volume" in comando:
        setVolume(comando)

       if any(word in comando for word in messages["commands"]["search"]):
          if "youtube" in comando or youtubeopen:
            risultati = cerca_youtube(comando, max_risultati=5)
            for url in risultati:
                webbrowser.open(url)

       if any(word in comando for word in messages["commands"]["getAI"]) and "youtube" not in comando:
          response = get_groq_response(comando)
          Process(target=notes, args=(response,), daemon=True).start()

    # Routine principale
    if not attivo:
        if wakeword in comando:
            attivo = True
            scrivistatus()
            if comando.strip() == wakeword:
                rispondi_e_parla(random.choice(listreplybot))
            else:
                esegui_com(comando)
    else:
        esegui_com(comando)



class OutputRedirector(QObject):
    newOutput = Signal(str)  # Segnale che invia l'output alla UI

    def __init__(self, parent=None):
        super().__init__(parent)

    def write(self, text):
        if text.strip():
            self.newOutput.emit(text.strip())  # Invia il testo alla UI

    def flush(self):
        pass  # Necessario per compatibilità con sys.stdout

    @Slot(str)
    def sendCommand(self, command):
        global attivo
        """Riceve il comando dal QML ed esegue l'azione corrispondente."""
        #self.newOutput.emit(f"Comando ricevuto: {command}")

        try:
            attivo = True
            comrecon(command)  # Esegue comrecon senza aspettare un ritorno
        except Exception as e:
            self.newOutput.emit(messages["error_messages"]["called_process_error"].format(e=e))




def listacomandi():
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    #aggiunge dati dell'app per il salvataggio'
    app.setOrganizationName("TecnoMas")
    app.setOrganizationDomain("tecnomas.engineering.com")
    app.setApplicationName("listacomandi")

    outputRedirector = OutputRedirector()
    sys.stdout = outputRedirector  # Reindirizza stdout alla nostra classe

    engine.rootContext().setContextProperty("outputRedirector", outputRedirector)
    engine.load(main_path / 'ui/listcom.qml')

    if not engine.rootObjects():
        sys.exit(-1)
    print(messages["other_messages"]["waiting_wakeword"].format(botname=botname))
    app.exec()



def listen():
    """Ciclo principale di ascolto."""
    global time_start,parla_sintesi


    with sr.Microphone() as source:
       #recognizer.adjust_for_ambient_noise(source, duration=1.0) #crea problemi di sensibilità
       Thread(target=listacomandi,daemon=True).start() #thread per ui con lista comandi


       while True:
            try:
                #lasciato in questa posizione consente di essere eseguito perioricamente senza creare loop
                Thread(target=downtime_control, daemon=True).start() #thread per controllo stato assistente

                #Sequenza senza uso di thread
                audio = recognizer.listen(source,timeout=5)
                comando = recognizer.recognize_google(audio,language="it-IT,en-US").lower()
                comrecon(comando)

            except sr.UnknownValueError:
               pass
            except sr.RequestError:
               pass
            except sr.WaitTimeoutError:
               pass
               #print ("Tempo scaduto in attesa della frase.Riprovo")



#non viene eseguita la  funzione se caricata nello script main.py
if __name__ == "__main__":
    listen()


