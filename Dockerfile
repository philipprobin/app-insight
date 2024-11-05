# Basis-Image verwenden (Python 3.11)
FROM python:3.11-slim


# Arbeitsverzeichnis erstellen und setzen
WORKDIR /app

# Anforderungen kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Firebase Admin SDK key file from your host to the Docker container
# Copy the Firebase Admin SDK key file into the Docker image
COPY .firebase-adminsdk.json /app/firebase-adminsdk.json

# Projektdateien in das Image kopieren
COPY . .

# Set environment variable for Firebase credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-adminsdk.json


# Offenlegung des Ports (optional, wenn du Flask oder FastAPI verwendest)
EXPOSE 8080

# Startbefehl für die Hauptdatei (ersetze 'main.py' durch die Datei, die dein Programm startet)
CMD ["python", "server.py"]

