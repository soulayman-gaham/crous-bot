from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d’environnement
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=2.1603044_45.9292956_2.2136084_45.8588518"

# === Scraper ===
def get_nombre_logements():
    try:
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        titre = soup.select_one("h2.SearchResults-desktop")
        if not titre:
            print("⚠️ Aucun titre détecté")
            return 0

        texte = titre.text.strip()
        print("🔍 Titre trouvé :", texte)

        if texte.startswith("Aucun"):
            return 0

        try:
            nb = int(texte.split(" ")[0])
            return nb
        except ValueError:
            print("❌ Erreur : nombre de logements non interprétable")
            return 0
    except Exception as e:
        print("❌ Erreur de scraping :", e)
        return 0

# === Envoi message Telegram ===
def envoyer_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        print("✅ Message envoyé")
    except Exception as e:
        print("❌ Erreur Telegram :", e)

# === Boucle principale ===
def verifier_logements():
    print("🔁 Recherche de logement...")
    nb = get_nombre_logements()
    if nb > 0:
        envoyer_message(f"🏠 <b>{nb} logement(s) disponible(s)</b> dans la zone !\n\n🔗 <a href='{URL}'>Voir sur le site</a>")

# === Message quotidien à 21h ===
def envoyer_presence():
    heure = datetime.now().strftime("%H:%M:%S")
    envoyer_message(f"✅ Le bot est toujours actif à {heure}")

# === Scheduler en boucle ===
def scheduler_loop():
    schedule.every(5).minutes.do(verifier_logements)
    schedule.every().day.at("21:00").do(envoyer_presence)

    while True:
        schedule.run_pending()
        time.sleep(1)

# === Démarrage du scheduler dans un thread ===
t = Thread(target=scheduler_loop)
t.daemon = True
t.start()

# === Flask bidon pour Render ===
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot de surveillance CROUS actif !"

if __name__ == "__main__":
    # Démarre le serveur sur le port que Render attend (par défaut 10000 ou 8080)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
