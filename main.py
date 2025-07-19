import requests
import time
import os

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?occupationModes=alone&bounds=3.0532561_45.8183838_3.1721761_45.7556941"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ALERTED = False

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(telegram_url, data=payload)

def check_availability():
    global ALERTED
    try:
        response = requests.get(URL)
        data = response.json()
        if data and len(data) > 0 and not ALERTED:
            message = f"🏠 <b>{len(data)} logement(s) dispo</b> à Clermont-Ferrand !\n🔗 <a href='{URL}'>Voir</a>"
            send_telegram_message(message)
            ALERTED = True
        elif len(data) == 0:
            ALERTED = False
    except Exception as e:
        print("Erreur:", e)

while True:
    check_availability()
    time.sleep(300)