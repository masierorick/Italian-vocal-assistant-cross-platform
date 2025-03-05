import sys
import os
import json
from pathlib import Path
import signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine,QQmlComponent, QmlElement
from PySide6.QtCore import QObject,Signal,Slot
from PySide6.QtWidgets import QApplication

#Percorsi principali
main_path = Path.cwd().parent
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = main_path / "config/config.json"

os.environ["QT_QPA_PLATFORM"] = "xcb"


class OutputRedirector(QObject):
    newOutput = Signal(str)

    def write(self, text):
        if text.strip():
            self.newOutput.emit(text.strip())

    def flush(self):
        pass

class ProcessManager(QObject):
    def __init__(self):
        super().__init__()



    @Slot()
    def checkColor(self):
        import re
        pattern = r'(\w+)\s*=\s*(.*)'
        filestatus = os.path.join(main_path, "script", "status.py")

        root_object = engine.rootObjects()[0]
        botname_text = root_object.findChild(QObject, "botname")

        with open(filestatus, 'r') as file:
            for line in file:
                match = re.match(pattern, line.strip())
                if match:
                    variabile = match.group(1)
                    if "attivo" in variabile:
                        attivo = match.group(2)
                        botname_text.setProperty("color", "red" if attivo == "True" else "white")

def run_app():


    with open(config_path, "r") as file:
          config_data = json.load(file)

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("TecnoMas")
    app.setOrganizationDomain("tecnomas.engineering.com")
    app.setApplicationName("uniwindow")

    process_manager = ProcessManager()
    outputRedirector = OutputRedirector()
    sys.stdout = outputRedirector

    global engine
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("processManager", process_manager)
    engine.rootContext().setContextProperty("outputRedirector", outputRedirector)
    engine.rootContext().setContextProperty("configData", config_data)

    engine.load(os.path.join(main_path, "ui/uniwindow.qml"))

    if not engine.rootObjects():
        print("Errore: impossibile caricare il file QML.")
        sys.exit(-1)

    app.exec()

if __name__ == "__main__":
        #print(os.path.join(main_path, "script", "status.py"))
        run_app()
