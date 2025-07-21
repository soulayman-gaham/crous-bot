import requests
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=0.6105136871337891_44.209464972561626_0.6345033645629884_44.18254249006941"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

@app.route("/")
def check_availability():
    try:
        response = requests.get(URL)
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
