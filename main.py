#File principale per assistente vocale
#Realizzato da Masiero Riccardo
#email: masierorick@gmail.com

#versione 2.4
#reso cross platform la ricerca dei programmi nei vari sistemi operativi Windows - Linux - Mac
#reso cross platform e adatto a tutti i browser la ricerca dei bookmarks nel browser predefinito
# inserita funzione per permettere a ui.qml di leggere il nomebot dal file json in config.

import os
import platform
import json
import signal
import shutil
import sqlite3
import sys
import multiprocessing
from multiprocessing import Process
import subprocess
from script.assistente import listen
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine,QQmlComponent, QmlElement
from PySide6.QtCore import QObject,Slot
from pathlib import Path


#variabili globali
current_dir = os.path.dirname(os.path.abspath(__file__))
listaprogrammi = current_dir + "/data/listaprogrammi"
listabookmarks = current_dir + "/data/bookmarks"
attivo = False




def get_installed_programs():
    #Configurazione cross platform
    system = platform.system()
    programs = set()  # Usa un set per evitare duplicati

    if system == "Linux":
        paths = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith(".desktop"):
                        file_path = os.path.join(path, file)
                        try:
                            with open(file_path, "r") as f:
                                name, exec_command = None, None
                                for line in f:
                                    if line.startswith("Name="):
                                        name = line.split("=", 1)[1].strip()
                                    if line.startswith("Exec="):
                                        exec_command = line.split("=", 1)[1].strip().split("%")[0]
                                    if name and exec_command:
                                        programs.add((name, exec_command))
                                        break
                        except Exception as e:
                            print(f"Errore leggendo il file {file_path}: {e}")

    elif system == "Windows":
        import winreg
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, subkey in reg_paths:
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey_handle:
                                name, _ = winreg.QueryValueEx(subkey_handle, "DisplayName")
                                exe_path, _ = winreg.QueryValueEx(subkey_handle, "InstallLocation")
                                if name and exe_path:
                                    programs.add((name, exe_path))
                        except OSError:
                            continue
            except OSError:
                continue

    elif system == "Darwin":  # macOS
        paths = [
            "/Applications",
            os.path.expanduser("~/Applications")
        ]
        for path in paths:
            if os.path.exists(path):
                programs.update(
                    (app[:-4], os.path.join(path, app))
                    for app in os.listdir(path) if app.endswith(".app")
                )

    else:
        raise NotImplementedError(f"Sistema operativo {system} non supportato")

    return sorted(programs)


def get_default_browser():
    system = platform.system()
    if system == "Windows":
        from winreg import OpenKey, HKEY_CURRENT_USER, QueryValueEx
        try:
            with OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                return QueryValueEx(key, "ProgId")[0]
        except Exception:
            return None
    elif system == "Darwin":
        try:
            return os.popen("/usr/bin/defaults read com.apple.LaunchServices/com.apple.launchservices.secure | grep -i http").read()
        except Exception:
            return None
    else:  # Linux
        try:
            return os.popen("xdg-settings get default-web-browser").read().strip()
        except Exception:
            return None


def get_browser_bookmarks():
    browser = get_default_browser().lower()
    user_home = Path.home()
    bookmarks = []

    if "chrome" in browser or "chromium" in browser:
        chrome_path = user_home / "AppData/Local/Google/Chrome/User Data/Default/Bookmarks" if platform.system() == "Windows" else user_home / ".config/google-chrome/Default/Bookmarks"
        if chrome_path.exists():
            with open(chrome_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("roots", {}).values():
                    bookmarks.extend(extract_chrome_bookmarks(item))

    elif "firefox" in browser:
        firefox_path = user_home / "AppData/Roaming/Mozilla/Firefox/Profiles" if platform.system() == "Windows" else user_home / ".mozilla/firefox"
        if firefox_path.exists():
            for profile in firefox_path.iterdir():
                places_db = profile / "places.sqlite"
                if places_db.exists():
                    bookmarks.extend(extract_firefox_bookmarks(places_db))
                    break

    elif "edge" in browser:
        edge_path = user_home / "AppData/Local/Microsoft/Edge/User Data/Default/Bookmarks"
        if edge_path.exists():
            with open(edge_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("roots", {}).values():
                    bookmarks.extend(extract_chrome_bookmarks(item))

    elif "vivaldi" in browser:
        vivaldi_path = user_home / "AppData/Local/Vivaldi/User Data/Default/Bookmarks" if platform.system() == "Windows" else user_home / ".config/vivaldi/Default/Bookmarks"
        if vivaldi_path.exists():
            with open(vivaldi_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("roots", {}).values():
                    bookmarks.extend(extract_chrome_bookmarks(item))

    return bookmarks


def extract_chrome_bookmarks(data):
    bookmarks = []
    if isinstance(data, dict):
        if data.get("type") == "url":
            bookmarks.append({"name": data["name"], "url": data["url"]})
        if "children" in data:
            for child in data["children"]:
                bookmarks.extend(extract_chrome_bookmarks(child))
    return bookmarks


def extract_firefox_bookmarks(db_path):
    temp_db = db_path.parent / "places_temp.sqlite"
    shutil.copy2(db_path, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT moz_bookmarks.title, moz_places.url FROM moz_bookmarks JOIN moz_places ON moz_bookmarks.fk = moz_places.id")
    bookmarks = [{"name": row[0], "url": row[1]} for row in cursor.fetchall() if row[0] and row[1]]
    conn.close()
    temp_db.unlink()
    return bookmarks

def runassistente():
    listen()

def main():
   global pid1,pid2,engine,current_dir,attivo

   #controllo sistema operativo utilizzato
   system = platform.system()
   print(f"System: {system}")


   programs = get_installed_programs()
   with open(listaprogrammi, 'w') as f:
      for name, command in programs:
         f.write(f"{name}={command}\n")
      f.close()

   #ottenimento bookmarks da vivaldi
   bookmarks = get_browser_bookmarks()
   if bookmarks:
      with open (listabookmarks, 'w') as file:
          for bookmark in bookmarks:
            #print(f"{bookmark.get('name')}: {bookmark.get('url')}")
            file.write(f"{bookmark.get('name')}={bookmark.get('url')}\n")
          file.close()
   else:
        print("Nessun segnalibro trovato.")


   #scrittura nel file stastus.py attivo = false
   with open(current_dir + "/script/status.py", 'w') as f:
     f.write(f"{"attivo"} = {attivo}\n")

   try:
     (p2 := Process(name='assistente', target=runassistente)).start()

     with open(current_dir + "/script/pid.py", 'w') as f:
       f.write(f"{"pid2"} = {p2.pid}\n")
       f.close()

   except (SystemExit, KeyboardInterrupt):
      os.kill(p2.pid, signal.SIGTERM)


#avvio processo principale chiamando la funzione main
if __name__ == '__main__':

   main()
