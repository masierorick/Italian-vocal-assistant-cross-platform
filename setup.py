from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import shutil
import subprocess

class PostInstallCommand(install):
    """Comando personalizzato per installare il file .desktop dopo l'installazione."""

    def run(self):
        install.run(self)  # Chiama il metodo di installazione originale
        user_home = os.path.expanduser("~")
        autostart_dir = os.path.join(user_home, ".config", "autostart")
        applications_dir = os.path.join(user_home, ".local", "share", "applications")

        # Percorso del file .desktop sorgente
        source_file = os.path.join(os.path.dirname(__file__), "resources", "AI.desktop")

        # Crea le directory, se non esistono
        os.makedirs(autostart_dir, exist_ok=True)
        os.makedirs(applications_dir, exist_ok=True)

        # Copia il file .desktop
        shutil.copy(source_file, autostart_dir)
        shutil.copy(source_file, applications_dir)
        print("File .desktop installati con successo!")

def install_portaudio():
    """Installa automaticamente PortAudio prima di installare i pacchetti Python"""
    try:
        if sys.platform.startswith("linux"):
            subprocess.run(["sudo", "apt", "install", "-y", "portaudio19-dev"], check=True)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["brew", "install", "portaudio"], check=True)
        elif sys.platform == "win32":
            print("⚠️ Su Windows, installa PortAudio manualmente da http://www.portaudio.com/download.html")
    except Exception as e:
        print(f"Errore durante l'installazione di PortAudio: {e}")

# Installare PortAudio prima di procedere con l'installazione delle dipendenze Python
install_portaudio()


setup(
    name="Assistente",
    version="3.0",
    author="Masiero Riccardo",
    author_email="tecnomas.engneering@gmail.com",
    description="assistente vocale in italiano",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuo_account/my_project",
    packages=find_packages(),              # Cerca automaticamente i pacchetti
    include_package_data=True,
    package_data={
      "assistente": [ #Specifica i file extra da includere
              "ui/*.gif",
              "ui/*.qml",
              "ui/*.png",
              "data/*.*",
              "data/*.csv",
              "script/.env",
              "config/*.json"
            ],

    },
    install_requires=[ # Specifica le dipendenze
        "comtypes>=1.4.9",
        "google_api_python_client>=2.154.0",
        "groq>=0.18.0",
        "openai>=1.61.0",
        "gTTS>=2.5.4",
        "playsound>=1.3.0",
        "PySide6>=6.8.0.2",
        "PySide6_Addons>=6.8.1",
        "PySide6_Essentials>=6.8.1",
        "python-dotenv>=1.0.1",
        "setuptools>=75.6.0",
        "SpeechRecognition>=3.11.0",
        "pyproject-toml==0.1.0",
        "PyAudio>=0.2.14",

    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",              # Versione minima di Python
)
