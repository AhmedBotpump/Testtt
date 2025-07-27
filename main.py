import os, time, requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

PUMP_API = "https://pump.fun/api/tokens"
BONK_API = "https://bonk.fun/api/tokens"
RUGCHECK_API = "https://api.rugcheck.xyz/tokens/"

seen = set()

def check_safety(ca):
    try:
        res = requests.get(f"{RUGCHECK_API}{ca}")
        return res.json().get("safety", {}).get("verdict", "UNKNOWN")
    except:
        return "UNKNOWN"

def fetch_all(api_url):
    try:
        r = requests.get(api_url)
        return r.json().get("tokens", [])[:10]
    except:
        return []

def alert(token, source):
    ca = token.get("address")
    name = token.get("name")
    mc = round(float(token.get("marketCapUsd", 0)))
    liq = round(float(token.get("liquidityUsd", 0)))

    safety = check_safety(ca)
    if safety != "GOOD" or mc > 7000 or liq < 500:
        return

    msg = (f"🚀 [{source.upper()}] عملة جديدة!\n\n"
           f"👤 الاسم: {name}\n"
           f"💰 القيمة السوقية: ${mc}\n"
           f"💧 السيولة ≈ {liq} USD\n"
           f"🛡️ الأمان: {safety}\n"
           f"🔗 https://{source}.fun/token/{ca}\n\n"
           f"🚀 [NEW] Token ({source.upper()})\n"
           f"Name: {name}, Market Cap: ${mc}, Liquidity: ${liq}, Safety: {safety}")
    bot.send_message(chat_id=CHAT_ID, text=msg)

def main_loop():
    while True:
        for platform, api in [("pump", PUMP_API), ("bonk", BONK_API)]:
            for t in fetch_all(api):
                ca = t.get("address")
                if ca and ca not in seen:
                    seen.add(ca)
                    alert(t, platform)
        time.sleep(20)

if __name__ == "__main__":
    main_loop()
