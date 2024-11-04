# Basis-Image verwenden (Python 3.11)
FROM python:3.11-slim


# Arbeitsverzeichnis erstellen und setzen
WORKDIR /app

# Anforderungen kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien in das Image kopieren
COPY . .

# Offenlegung des Ports (optional, wenn du Flask oder FastAPI verwendest)
EXPOSE 8080

# Startbefehl für die Hauptdatei (ersetze 'main.py' durch die Datei, die dein Programm startet)
CMD ["python", "server.py"]

