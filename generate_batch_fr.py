
import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()
print("🔁 Script Nova — TEST 1 question complète (traduction + vidéo + update)")

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
    for _ in range(30):
        r = requests.get(f"https://api.heygen.com/v1/video_status?video_id={video_id}", headers=headers)
        if r.status_code == 200:
            url = r.json().get("data", {}).get("video_url")
            if url:
                return url
        time.sleep(5)
    return None

def upload_to_supabase(video_bytes, video_id):
    filename = f"video_question_fr/{video_id}.mp4"
    url = f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/nova-videos/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4"
    }
    r = requests.post(url, headers=headers, data=video_bytes)
    if r.status_code in [200, 201]:
        return f"https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public/nova-videos/{filename}"
    else:
        print(f"❌ Upload failed: {r.status_code} - {r.text}")
        return None

def update_db(row_id, updates):
    url = f"{SUPABASE_TABLE_URL}?id=eq.{row_id}"
    r = requests.patch(url, headers=headers_db, data=json.dumps(updates))
    if r.status_code not in [200, 204]:
        print(f"❌ DB update failed for {row_id} : {r.status_code} - {r.text}")

def translate(text, lang):
    prompt = f"Traduire en {lang} ce texte professionnellement :\n{text}"
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Tu es un traducteur professionnel."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"].strip()
    else:
        print(f"❌ Traduction {lang} échouée : {r.status_code}")
        return None

def fetch_one_row():
    url = f"{SUPABASE_TABLE_URL}?select=*&limit=20"
    r = requests.get(url, headers=headers_db)
    rows = r.json() if r.status_code == 200 else []
    for row in rows:
        if row.get("question_fr") and not row.get("video_question_fr") and row.get("status_video_fr") != "ok":
            return row
    return None

def main():
    row = fetch_one_row()
    if not row:
        print("❌ Aucune question valide trouvée.")
        return

    qid = row["id"]
    text = row["question_fr"]
    print(f"🎤 Traitement de : {qid} → {text}")
    try:
        update_db(qid, {"status_video_fr": "pending"})

        en = translate(text, "anglais")
        es = translate(text, "espagnol")
        print(f"🌍 EN : {en}")
        print(f"🌍 ES : {es}")
        update_db(qid, {"question_en": en, "question_es": es})

        payload = {
            "video_inputs": [
                {
                    "voice": {"type": "text", "input_text": text, "voice_id": HEYGEN_VOICE_FR},
                    "character": {"type": "talking_photo", "talking_photo_id": HEYGEN_TALKING_PHOTO_ID},
                    "background": {"type": "color", "value": "#FFFFFF"}
                }
            ]
        }
        headers = {"Authorization": f"Bearer {HEYGEN_API_KEY}", "Content-Type": "application/json"}
        r = requests.post("https://api.heygen.com/v2/video/generate", headers=headers, json=payload)

        if r.status_code != 200:
            print(f"❌ Heygen error: {r.text}")
            update_db(qid, {"status_video_fr": "error"})
            return

        video_id = r.json()["data"]["video_id"]
        print(f"⏳ Attente vidéo {video_id}...")
        video_url = wait_for_video(video_id)
        if not video_url:
            update_db(qid, {"status_video_fr": "error"})
            return

        video_bytes = requests.get(video_url).content
        final_url = upload_to_supabase(video_bytes, video_id)
        if final_url:
            update_db(qid, {
                "video_question_fr": final_url,
                "video_id_fr": video_id,
                "status_video_fr": "ok"
            })
            print(f"✅ Vidéo uploadée : {final_url}")
        else:
            update_db(qid, {"status_video_fr": "error"})

    except Exception as e:
        print(f"❌ Erreur pour {qid} : {e}")
        update_db(qid, {"status_video_fr": "error"})

if __name__ == "__main__":
    main()
