
import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()
print("🔁 Script Nova lancé depuis Render...")

SUPABASE_PROJECT_ID = os.getenv("SUPABASE_URL").split("//")[1].split(".")[0]
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_TALKING_PHOTO_ID = os.getenv("HEYGEN_TALKING_PHOTO_ID")
HEYGEN_VOICE_FR = os.getenv("HEYGEN_VOICE_FR")
SUPABASE_TABLE_URL = os.getenv("SUPABASE_URL") + "/rest/v1/nova_questions"

headers_db = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

def fetch_questions():
    res = requests.get(f"{SUPABASE_TABLE_URL}?select=*", headers=headers_db)
    if res.status_code != 200:
        print(f"❌ Erreur Supabase : {res.status_code} - {res.text}")
        return []
    all_rows = res.json()
    print(f"📦 {len(all_rows)} ligne(s) reçue(s) depuis Supabase.")
    for r in all_rows:
        print(f"🆔 {r.get('id')} — Q: {r.get('question_fr')} / Vidéo: {r.get('video_question_fr')}")
    rows = [
        row for row in all_rows
        if row.get("question_fr") and (not row.get("video_question_fr") or row.get("video_question_fr") == "")
    ]
    print(f"🎯 {len(rows)} question(s) détectées à traiter.")
    return rows

def main():
    questions = fetch_questions()
    if not questions:
        print("⚠️ Aucun traitement effectué. Fin du script.")
        return
    for row in questions:
        print(f"🚧 À faire : {row['id']}")

if __name__ == "__main__":
    main()
