from flask import Flask, render_template
from main import main
from utils import send_discord_alert
import traceback
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", message="👋 Welcome! Click /sync to start syncing.", songs=[])

@app.route("/sync")
def sync():
    try:
        message, songs = main()  # updated to return message and list of added songs
        return render_template("index.html", message=message, songs=songs)
    except Exception as e:
        traceback.print_exc()
        send_discord_alert(f"❌ Spotify sync failed:\n{str(e)}")
        return render_template("index.html", message=f"❌ Error occurred: {str(e)}", songs=[])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
