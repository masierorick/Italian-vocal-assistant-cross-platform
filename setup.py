from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import shutil

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

setup(
    name="assistente",
    version="1.0.0",
    author="Masiero Riccardo",
    author_email="masierorick@gmail.com",
    description="assistente vocale per neon kde",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tuo_account/my_project",
    packages=find_packages(),              # Cerca automaticamente i pacchetti
    include_package_data=True,
    package_data={
      "assistente": [ #Specifica i file extra da includere
              "ui/*.gif",
              "ui/*.qml",
              "data/*.*",
              "data/*.csv",
              "script/.env"
            ],

    },
    install_requires=[ # Specifica le dipendenze
        "beautifulsoup4>=4.12.3",
        "groq>=0.13.1",
        "gTTS>=2.5.4",
        "jsonpath_ng>=1.7.0",
        "playsound>=1.3.0",
        "pyradio>=0.5.2",
        "PySide6>=6.8.0.2",
        "PySide6_Addons>=6.8.1",
        "PySide6_Essentials>=6.8.1",
        "python-dotenv>=1.0.1",
        "radio>=0.1.3",
        "SpeechRecognition>=3.11.0",

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
