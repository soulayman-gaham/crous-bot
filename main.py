import requests
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?occupationModes=alone&bounds=3.0532561_45.8183838_3.1721761_45.7556941"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

@app.route("/")
def check_availability():
    try:
        response = requests.get(URL)
        content_type = response.headers.get("Content-Type", "")
        print("📥 Status HTTP :", response.status_code)
        print("📄 Content-Type :", content_type)

        if "application/json" not in content_type:
            return "❌ Erreur : la réponse n'est pas du JSON valide."

        data = response.json()

        if data and len(data) > 0:
            message = f"🏠 <b>{len(data)} logement(s) dispo</b> à Clermont-Ferrand !\n🔗 <a href='{URL}'>Voir</a>"
            send_telegram_message(message)
            return "✅ Logement(s) détecté(s) et message envoyé."
        else:
            return "❌ Aucun logement disponible."

    except Exception as e:
        return f"❌ Erreur: {e}"

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(telegram_url, data=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
