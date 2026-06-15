from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import requests

app = Flask(__name__)

BOT_TOKEN = "8716076962:AAHpIFuyq7Jq51Gy4Dj9PsPexClS-v04-Oo"
CHAT_ID = "723175483"

def telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# DB
conn = sqlite3.connect("orders.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT,
plate TEXT,
created_at TEXT
)
""")
conn.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/book", methods=["POST"])
def book():
    name = request.form["name"]
    phone = request.form["phone"]
    plate = request.form["plate"]

    cur.execute("""
    INSERT INTO orders(name, phone, plate, created_at)
    VALUES (?,?,?,?)
    """, (name, phone, plate, datetime.now().isoformat()))
    conn.commit()

    telegram(
        f"🦈 NEW BOOKING\n\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Plate: {plate}"
    )

    return "Booking successful ✔"

if __name__ == "__main__":
    app.run()