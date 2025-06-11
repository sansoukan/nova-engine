
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
print("🔁 Script Nova — LOG des lignes Supabase")

SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_TABLE_URL = os.getenv("SUPABASE_URL") + "/rest/v1/nova_questions"

headers_db = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def main():
    url = f"{SUPABASE_TABLE_URL}?select=*&limit=50"
    res = requests.get(url, headers=headers_db)
    if res.status_code != 200:
        print(f"❌ Supabase Error {res.status_code}: {res.text}")
        return

    rows = res.json()
    print(f"📦 {len(rows)} ligne(s) reçue(s)")

    for row in rows:
        print("—" * 50)
        print(f"🆔 {row.get('id')}")
        print(f"❓ FR: {row.get('question_fr')}")
        print(f"📼 VID: {row.get('video_question_fr')}")
        print(f"📊 STATUS: {row.get('status_video_fr')}")

if __name__ == "__main__":
    main()
