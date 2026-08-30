import re
import json
import urllib.request
import urllib.error
from FileStream.config import Telegram

def regex_fallback_parse(text: str):
    """
    Fallback regex parser when AI is unavailable or rate limited.
    Extracts title and lecture number from structured or unstructured text.
    """
    if not text:
        return {"title": "Untitled Lecture", "lecture_no": 999}
    
    # Try finding title from structured format like: ◇ Title » (Current) CURRENT - LECTURE - 27 BY AG SIR:
    title_match = re.search(r'(?:Title\s*»|Title\s*:)\s*([^\n]+)', text, re.IGNORECASE)
    raw_title = title_match.group(1).strip() if title_match else text.split('\n')[0].strip()

    # Clean up markdown / emoji clutter
    clean_title = re.sub(r'[*_~`✨❤️◇👤■►]', '', raw_title).strip()
    
    # Extract lecture number (e.g. LECTURE - 27, Lec 05, L-12, #27, etc.)
    lec_match = re.search(r'(?:LECTURE|Lec|L)\s*[-:]*\s*(\d+)', text, re.IGNORECASE)
    if not lec_match:
        lec_match = re.search(r'#(\d+)', text)
    if not lec_match:
        lec_match = re.search(r'\b(\d{1,3})\b', clean_title)

    lecture_no = int(lec_match.group(1)) if lec_match else 999

    return {
        "title": clean_title if clean_title else "Untitled Lecture",
        "lecture_no": lecture_no
    }

async def parse_lecture_info(caption_or_name: str):
    """
    Parses video caption or file name using Groq AI with key rotation.
    Returns dict: {"title": str, "lecture_no": int}
    """
    if not caption_or_name or not caption_or_name.strip():
        return {"title": "Untitled Lecture", "lecture_no": 999}

    text_to_parse = caption_or_name.strip()
    prompt = f"""Extract the clean lecture title and the lecture number from this text.
Text: "{text_to_parse}"

Respond ONLY with valid JSON in this exact format:
{{"title": "Clean Lecture Title Here", "lecture_no": 27}}
If no lecture number is explicitly found, default lecture_no to 999.
Do not include markdown or explanations."""

    # Try each key in Telegram.GROQ_API_KEYS
    for api_key in Telegram.GROQ_API_KEYS:
        if not api_key or not api_key.startswith("gsk_"):
            continue
        try:
            req_data = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    resp_body = json.loads(response.read().decode('utf-8'))
                    content = resp_body['choices'][0]['message']['content']
                    parsed = json.loads(content)
                    title = str(parsed.get('title', '')).strip()
                    try:
                        lec_no = int(parsed.get('lecture_no', 999))
                    except (ValueError, TypeError):
                        lec_no = 999

                    if title:
                        return {"title": title, "lecture_no": lec_no}
        except Exception as e:
            print(f"[Groq Parser] API key error: {e}, trying next key...")
            continue

    # Fallback if Groq API fails
    print("[Groq Parser] Falling back to regex parser...")
    return regex_fallback_parse(text_to_parse)
