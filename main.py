import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://trouverunlogement.lescrous.fr/tools/41/search?bounds=2.1603044_45.9292956_2.2136084_45.8588518"

def get_nombre_logements():
    try:
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

def envoyer_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        res = requests.post(url, data=data)
        res.raise_for_status()
        print("✅ Message envoyé")
    except Exception as e:
        print("❌ Erreur Telegram :", e)

def main():
    print("🔍 Vérification du nombre de logements...")
    nb = get_nombre_logements()
    if nb > 0:
        envoyer_message(f"🏠 <b>{nb} logement(s) disponible(s)</b> dans la zone !\n\n🔗 <a href='{URL}'>Voir sur le site</a>")
    else:
        print("⚠️ Aucun logement trouvé.")

if __name__ == "__main__":
    main()
