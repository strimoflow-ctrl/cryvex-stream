import json
import time
import urllib.request
import urllib.error
from FileStream.config import Telegram

async def push_pending_upload(file_id: str, title: str, lecture_no: int, stream_link: str, file_name: str, file_size: str):
    """
    Pushes a processed video item to Firebase Realtime DB under /pending_uploads
    """
    if not Telegram.FIREBASE_DATABASE_URL:
        print("[Firebase] No FIREBASE_DATABASE_URL configured.")
        return False

    db_url = Telegram.FIREBASE_DATABASE_URL.rstrip('/')
    url = f"{db_url}/pending_uploads.json"

    data = {
        "id": file_id,
        "title": title,
        "lecture_no": lecture_no,
        "stream_link": stream_link,
        "file_name": file_name,
        "file_size": file_size,
        "timestamp": int(time.time() * 1000)
    }

    try:
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 201):
                print(f"[Firebase] Pushed pending upload {file_id} successfully.")
                return True
    except Exception as e:
        print(f"[Firebase Error] Failed to push item to Firebase: {e}")
        return False
