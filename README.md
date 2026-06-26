<h1 align="center">Personal & Clean FileStreamBot</h1>

<p align='center'>
  A clean, lightweight Telegram Bot to generate high-speed direct download links for your personal files.<br>
  <b>👑 Maintained & Customized By: <a href="https://t.me/cryvex4">@cryvex4</a></b>
</p>

## 🌟 Key Features

- **Direct Download Links Only (`/dl/` route)**: No web players, no force subscribe, no multi-client bloat.
- **High Speed**: Directly streams files from Telegram servers via a clean aiohttp web server.
- **HTTPS Supported**: Ready for Render, Koyeb, Railway, Heroku, or VPS hosting.
- **MongoDB Free Tier Friendly**: Stores file records efficiently (approx. 500,000 files in 512 MB).

---

## ☁️ Render.com Deployment Guide

जब आप Render पर इसे होस्ट करेंगे (Web Service के तौर पर), तो आपको यह एनवायरनमेंट सेटिंग्स (Environment Variables) डालनी होंगी:

### 1. Build & Start Commands (Render Dashboard में डालें):
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `python -m FileStream`

### 2. Environment Variables (Config):
| Variable | Description / Example Value |
| :--- | :--- |
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API Hash |
| `BOT_TOKEN` | Bot Token from @BotFather |
| `DATABASE_URL` | MongoDB Atlas Connection URI |
| `FQDN` | आपका Render डोमेन (जैसे: `cryvex-stream.onrender.com`) |
| `HAS_SSL` | `True` |
| `NO_PORT` | `True` |
| `PORT` | `10000` (Render डिफ़ॉल्ट रूप से वेब सर्विसेज़ के लिए पोर्ट असाइन करता है) |
| `OWNER_ID` | आपका टेलीग्राम User ID |

*(नोट: Render पर फ्री टियर में 15 मिनट बाद सर्विस स्लीप में चली जाती है, इसलिए कोई भी अपटाइम मॉनिटर जैसे UptimeRobot को अपने `https://your-app.onrender.com/status` पर पिंग करने के लिए लगा दें)*

---

## 🚀 How to Run Locally

```sh
git clone https://github.com/strimoflow-ctrl/cryvex-stream.git
cd cryvex-stream
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m FileStream
```

<p align="center">
  <b>⚡ Powered by @cryvex4</b>
</p>
