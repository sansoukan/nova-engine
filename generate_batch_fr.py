
import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()
print("🔁 Script Nova — récupération vidéo via /v1/video/{video_id} ✔")

SUPABASE_PROJECT_ID = os.getenv("SUPABASE_URL").split("//")[1].split(".")[0]
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_TALKING_PHOTO_ID = os.getenv("HEYGEN_TALKING_PHOTO_ID")
HEYGEN_VOICE_FR = os.getenv("HEYGEN_VOICE_FR")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_TABLE_URL = os.getenv("SUPABASE_URL") + "/rest/v1/nova_questions"

headers_db = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def wait_for_video(video_id):
    headers = {"Authorization": f"Bearer {HEYGEN_API_KEY}"}
    print(f"⏳ Vérification via /v1/video/{video_id}")
    for attempt in range(30):
        r = requests.get(f"https://api.heygen.com/v1/video/{video_id}", headers=headers)
        if r.status_code == 200:
            data = r.json().get("data", {})
            video_url = data.get("video_url")
            print(f"⏳ Tentative {attempt+1}: {'✅' if video_url else '⏳ Pas encore dispo'}")
            if video_url:
                return video_url
        time.sleep(5)
    return None

# Le reste du script reste inchangé — à compléter avec le bloc de traitement standard.
