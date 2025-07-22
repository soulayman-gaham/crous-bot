from flask import Flask
from threading import Thread
import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import schedule

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=3.0532561_45.8183838_3.1721761_45.7556941"

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot en ligne 🚀"

def envoyer_message(msg):
    print(f"[{datetime.now()}] 📬 Envoi du message : {msg}")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        print(f"[{datetime.now()}] ✅ Message envoyé")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Erreur Telegram :", e)

def get_nombre_logements():
    try:
        print(f"[{datetime.now()}] 🔍 Vérification des logements...")
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        titre = soup.select_one("h2.SearchResults-desktop")
        if not titre:
            print("⚠️ Aucun titre trouvé")
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
        print(f"❌ Erreur de scraping : {e}")
        return 0

def check_and_alert():
    nb = get_nombre_logements()
    if nb > 0:
        envoyer_message(f"🏠 <b>{nb} logement(s) dispo</b> !\n🔗 <a href='{URL}'>Voir</a>")
    else:
        print(f"[{datetime.now()}] Aucun logement trouvé.")

def daily_ping():
    envoyer_message("✅ Le bot est toujours actif à 21h.")

def scheduler_loop():
    print("🎯 Démarrage de la boucle de vérification")
    schedule.every(5).minutes.do(check_and_alert)
    schedule.every().day.at("21:00").do(daily_ping)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Démarrer la boucle dans un thread
    Thread(target=scheduler_loop).start()
    # Lancer Flask (port pour Render)
    app.run(host="0.0.0.0", port=10000)
