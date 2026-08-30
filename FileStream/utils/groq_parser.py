import re
import json
import urllib.request
import urllib.error
from FileStream.config import Telegram

def regex_fallback_parse(text: str):
    """
    Fallback regex parser when AI is unavailable or rate limited.
    Extracts lecture number ignoring 'Index' markers.
    Returns title as 'Lecture XX' and lecture_no as int.
    """
    if not text:
        return {"title": "Lecture 01", "lecture_no": 1}
    
    # Remove lines or text containing "Index »" or "Index:" or "Index" to prevent picking index as lecture_no
    clean_text = re.sub(r'(?i)◇?\s*Index\s*[»:]*\s*\d+', '', text)

    # 1. Check for LECTURE - 27, Lec 05, L-12, Class 22, Live Class 22, etc.
    lec_match = re.search(r'(?:LECTURE|Lec|Class|L)\s*[-:]*\s*(\d+)', clean_text, re.IGNORECASE)
    
    # 2. Check for Date format like 22 May, 13 May (often indicates class/lecture number)
    if not lec_match:
        lec_match = re.search(r'\b(\d{1,2})\s*(?:May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar|Apr)\b', clean_text, re.IGNORECASE)

    # 3. Check for standalone numbers
    if not lec_match:
        lec_match = re.search(r'#(\d+)', clean_text)
    if not lec_match:
        lec_match = re.search(r'\b(\d{1,2})\b', clean_text)

    if lec_match:
        lecture_no = int(lec_match.group(1))
    else:
        lecture_no = 999

    if lecture_no != 999:
        title = f"Lecture {lecture_no:02d}" if lecture_no < 10 else f"Lecture {lecture_no}"
    else:
        title = "Lecture"

    return {
        "title": title,
        "lecture_no": lecture_no
    }

async def parse_lecture_info(caption_or_name: str):
    """
    Parses video caption or file name using Groq AI with key rotation.
    Returns dict: {"title": "Lecture XX", "lecture_no": int}
    """
    if not caption_or_name or not caption_or_name.strip():
        return {"title": "Lecture 01", "lecture_no": 1}

    text_to_parse = caption_or_name.strip()
    prompt = f"""You are a smart lecture parser.
Text: "{text_to_parse}"

RULES:
1. Ignore any "Index » 187" or "Index: N" lines. "Index" is NOT the lecture number.
2. Find the true Lecture or Class number from terms like "LECTURE - 27", "(Live Class) 22 May", "Chemistry Class 22", "Lec 05", etc.
3. If the date specifies "22 May" or "13 May" or "Class 22", the lecture number is 22 or 13.
4. Set "lecture_no" to the integer lecture number found (e.g. 22 or 27 or 13). If no lecture number found, set lecture_no to 999.
5. Format "title" strictly as "Lecture XX" where XX is the lecture number padded with 2 digits if single digit (e.g., "Lecture 01", "Lecture 02", "Lecture 13", "Lecture 22").

Respond ONLY with valid JSON:
{{"title": "Lecture 22", "lecture_no": 22}}"""

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
                    try:
                        lec_no = int(parsed.get('lecture_no', 999))
                    except (ValueError, TypeError):
                        lec_no = 999

                    if lec_no != 999:
                        title = f"Lecture {lec_no:02d}" if lec_no < 10 else f"Lecture {lec_no}"
                    else:
                        title = str(parsed.get('title', 'Lecture')).strip() or "Lecture"

                    return {"title": title, "lecture_no": lec_no}
        except Exception as e:
            print(f"[Groq Parser] API key error: {e}, trying next key...")
            continue

    # Fallback if Groq API fails
    print("[Groq Parser] Falling back to regex parser...")
    return regex_fallback_parse(text_to_parse)
