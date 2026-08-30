from os import environ as env
from dotenv import load_dotenv

load_dotenv()

class Telegram:
    API_ID = int(env.get("API_ID"))
    API_HASH = str(env.get("API_HASH"))
    BOT_TOKEN = str(env.get("BOT_TOKEN"))
    OWNER_ID = int(env.get('OWNER_ID', '7978482443'))
    WORKERS = int(env.get("WORKERS", "6"))  # 6 workers = 6 commands at once
    DATABASE_URL = str(env.get('DATABASE_URL'))
    UPDATES_CHANNEL = str(env.get('UPDATES_CHANNEL', "Telegram"))
    SESSION_NAME = str(env.get('SESSION_NAME', 'FileStream'))
    FORCE_SUB_ID = env.get('FORCE_SUB_ID', None)
    FORCE_SUB = env.get('FORCE_UPDATES_CHANNEL', False)
    FORCE_SUB = True if str(FORCE_SUB).lower() == "true" else False
    SLEEP_THRESHOLD = int(env.get("SLEEP_THRESHOLD", "60"))
    FILE_PIC = env.get('FILE_PIC', "https://graph.org/file/5bb9935be0229adf98b73.jpg")
    START_PIC = env.get('START_PIC', "https://graph.org/file/290af25276fa34fa8f0aa.jpg")
    VERIFY_PIC = env.get('VERIFY_PIC', "https://graph.org/file/736e21cc0efa4d8c2a0e4.jpg")
    MULTI_CLIENT = False
    FLOG_CHANNEL = int(env.get("FLOG_CHANNEL", None))   # Logs channel for file logs
    ULOG_CHANNEL = int(env.get("ULOG_CHANNEL", None))   # Logs channel for user logs
    MODE = env.get("MODE", "primary")
    SECONDARY = True if MODE.lower() == "secondary" else False
    AUTH_USERS = list(set(int(x) for x in str(env.get("AUTH_USERS", "")).split()))
    GROQ_API_KEYS = [
        env.get("GROQ_API_KEY_1", ""),
        env.get("GROQ_API_KEY_2", ""),
        env.get("GROQ_API_KEY_3", "")
    ]
    FIREBASE_DATABASE_URL = env.get("FIREBASE_DATABASE_URL", "https://nainoacademy-50f09-default-rtdb.firebaseio.com")

class Server:
    PORT = int(env.get("PORT", 8080))
    BIND_ADDRESS = str(env.get("BIND_ADDRESS", "0.0.0.0"))
    PING_INTERVAL = int(env.get("PING_INTERVAL", "1200"))
    
    _fqdn = str(env.get("FQDN", BIND_ADDRESS)).strip()
    if _fqdn.startswith("http://"):
        _fqdn = _fqdn[7:]
    elif _fqdn.startswith("https://"):
        _fqdn = _fqdn[8:]
    _fqdn = _fqdn.rstrip("/")

    HAS_SSL = str(env.get("HAS_SSL", "1" if ("onrender.com" in _fqdn or "railway.app" in _fqdn or "koyeb.app" in _fqdn) else "0").lower()) in ("1", "true", "t", "yes", "y")
    NO_PORT = str(env.get("NO_PORT", "1" if ("onrender.com" in _fqdn or "railway.app" in _fqdn or "koyeb.app" in _fqdn) else "0").lower()) in ("1", "true", "t", "yes", "y")

    FQDN = _fqdn
    URL = "http{}://{}{}/".format(
        "s" if HAS_SSL else "", FQDN, "" if NO_PORT else ":" + str(PORT)
    )




