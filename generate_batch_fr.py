
import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()
print("🔁 Script Nova — test 1 ligne avec wait_for_video() corrigé")

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
    print(f"⏳ Suivi de la vidéo {video_id}...")
    for attempt in range(30):
        r = requests.get(f"https://api.heygen.com/v1/video_status?video_id={video_id}", headers=headers)
        if r.status_code == 200:
            data = r.json().get("data", {})
            print(f"⏳ Tentative {attempt+1}: statut = {data.get('status')}")
            if data.get("status") == "done" and data.get("video_url"):
                return data.get("video_url")
        time.sleep(5)
    return None
