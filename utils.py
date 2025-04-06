import os
import requests
from dotenv import load_dotenv
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_discord_alert(message):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ No Discord webhook URL configured.")
        return

    try:
        data = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)

        if response.status_code != 204:
            print(f"⚠️ Discord webhook failed: {response.status_code} {response.text}")
        else:
            print("📣 Discord alert sent!")
    except Exception as e:
        print(f"🚨 Error sending Discord alert: {e}")
