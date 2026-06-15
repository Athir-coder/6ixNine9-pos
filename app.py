from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import os
import random
import requests

app = Flask(__name__)

# ---------------- TELEGRAM ----------------
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

# ---------------- CONFIG ----------------
CAR_TYPES = {"Sedan": 2000, "SUV": 2800, "Sport": 3500}
WRAP_TYPES = {"Matte": 500, "Glossy": 400, "Chrome": 900}
WASH = {"Basic Wash": 10, "Premium Wash": 20, "Full Detail": 40}
EXTRAS = {"Roof Wrap": 300, "Rim Wrap": 250, "Interior Trim": 200}
COLORS = {"Black": 0, "White": 0, "Red": 100, "Blue": 100}

BLOCKED_DATES = {"2026-01-01", "2026-02-10"}
MAX_BOOKINGS_PER_DAY = 5

# ---------------- DB PATH ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "orders.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
booking_id TEXT,
name TEXT,
phone TEXT,
plate TEXT,
appointment_date TEXT,
car_type TEXT,
color TEXT,
wrap_type TEXT,
wash_type TEXT,
extras TEXT,
total REAL,
created_at TEXT
)
""")
conn.commit()

# ---------------- HELPERS ----------------
def count_bookings(date):
    cur.execute("SELECT COUNT(*) FROM orders WHERE appointment_date=?", (date,))
    return cur.fetchone()[0]

def calculate_total(car, color, wrap, wash, extras):
    total = 0
    total += CAR_TYPES.get(car, 0)
    total += COLORS.get(color, 0)
    total += WRAP_TYPES.get(wrap, 0)
    total += WASH.get(wash, 0)
    for e in extras:
        total += EXTRAS.get(e, 0)
    return total

def generate_booking_id():
    return f"MS-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html",
        cars=CAR_TYPES,
        colors=COLORS,
        wraps=WRAP_TYPES,
        washes=WASH,
        extras=EXTRAS,
        blocked=BLOCKED_DATES
    )

@app.route("/book", methods=["POST"])
def book():
    name = request.form["name"]
    phone = request.form["phone"]
    plate = request.form["plate"]
    date = request.form["date"]

    car = request.form["car"]
    color = request.form["color"]
    wrap = request.form["wrap"]
    wash = request.form["wash"]

    extras = request.form.getlist("extras")

    # ---------------- VALIDATION ----------------
    if date in BLOCKED_DATES:
        return "Date blocked"

    if count_bookings(date) >= MAX_BOOKINGS_PER_DAY:
        return "Fully booked"

    total = calculate_total(car, color, wrap, wash, extras)
    booking_id = generate_booking_id()

    cur.execute("""
    INSERT INTO orders(
        booking_id, name, phone, plate,
        appointment_date, car_type, color,
        wrap_type, wash_type, extras,
        total, created_at
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        booking_id, name, phone, plate,
        date, car, color,
        wrap, wash, ",".join(extras),
        total, datetime.now().isoformat()
    ))

    conn.commit()

    # ---------------- TELEGRAM ALERT ----------------
    telegram(
        f"""🦈 NEW BOOKING

ID: {booking_id}
Name: {name}
Phone: {phone}
Plate: {plate}

Date: {date}
Car: {car}
Color: {color}
Wrap: {wrap}
Wash: {wash}
Extras: {extras}

TOTAL: RM {total}
"""
    )

    return f"Booking successful ✔ ID: {booking_id}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
