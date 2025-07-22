import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=2.1603044_45.9292956_2.2136084_45.8588518"

last_daily_message = None

def envoyer_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        print("✅ Message envoyé")
    except Exception as e:
        print("❌ Erreur Telegram :", e)

def get_nombre_logements():
    try:
        print("🔍 Recherche de logements...")  # <- log à chaque recherche
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        titre = soup.select_one("h2.SearchResults-desktop")
        if not titre:
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

def send_daily_alive_message():
    global last_daily_message
    now = datetime.now()
    if now.hour == 21 and (last_daily_message is None or last_daily_message.date() != now.date()):
        envoyer_message("🤖 Le bot est toujours actif et fonctionne normalement ✅")
        last_daily_message = now

while True:
    nb = get_nombre_logements()
    if nb > 0:
        envoyer_message(f"🏠 <b>{nb} logement(s) disponible(s)</b> dans la zone !\n\n🔗 <a href='{URL}'>Voir sur le site</a>")
    else:
        print("⚠️ Aucun logement trouvé.")

    send_daily_alive_message()
    time.sleep(300)  # 5 minutes
