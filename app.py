"""
6ixNine9 Motorsport Booking System
FIXED SQLITE + TELEGRAM + PDF + LOCKED DATE + 2 PANEL UI
"""

import sqlite3
import random
import os
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import requests

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

print("DB LOCATION:", os.path.abspath("orders.db"))

# ================= CONFIG =================
BOT_TOKEN = "8716076962:AAHpIFuyq7Jq51Gy4Dj9PsPexClS-v04-Oo"
CHAT_ID = "723175483"

CAR_TYPES = {"Sedan": 2000, "SUV": 2800, "Sport": 3500}
WRAP_TYPES = {"Matte": 500, "Glossy": 400, "Chrome": 900}
WASH = {"Basic Wash": 10, "Premium Wash": 20, "Full Detail": 40}
EXTRAS = {"Roof Wrap": 300, "Rim Wrap": 250, "Interior Trim": 200}
COLORS = {"Black": 0, "White": 0, "Red": 100, "Blue": 100}

BLOCKED_DATES = {"2026-01-01", "2026-02-10"}
MAX_BOOKINGS_PER_DAY = 5

# ================= FOLDER =================
os.makedirs("C:/6ixNine9_Invoices", exist_ok=True)

# ================= DB =================
conn = sqlite3.connect("orders.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
booking_id TEXT,
customer_name TEXT,
phone TEXT,
car_plate TEXT,
appointment_date TEXT,
car_type TEXT,
color TEXT,
wrap_type TEXT,
extras TEXT,
wash_package TEXT,
total REAL,
status TEXT,
created_at TEXT
)
""")
conn.commit()

# ================= TELEGRAM =================
def telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        pass

# ================= APP =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("6ixNine9 Motorsport Booking")
app.geometry("1200x800")

# ================= STATE =================
car_var = ctk.StringVar()
wrap_var = ctk.StringVar()
wash_var = ctk.StringVar()
color_var = ctk.StringVar()
extra_state = {k: False for k in EXTRAS}

# ================= HELPERS =================
def count_bookings(date):
    cur.execute("SELECT COUNT(*) FROM orders WHERE appointment_date=?", (date,))
    return cur.fetchone()[0]

def booking_id():
    return f"MS-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

def grand_total():
    return (
        CAR_TYPES.get(car_var.get(), 0) +
        WRAP_TYPES.get(wrap_var.get(), 0) +
        WASH.get(wash_var.get(), 0) +
        COLORS.get(color_var.get(), 0) +
        sum(EXTRAS[k] for k, v in extra_state.items() if v)
    )

# ================= TOGGLE =================
def toggle_extra(key, btn):
    extra_state[key] = not extra_state[key]
    btn.configure(fg_color="#1f6aa5" if extra_state[key] else "#2b2b2b")
    update_summary()

# ================= PDF =================
def generate_pdf(bid, name, phone, plate, date, total):
    filename = os.path.join("invoices", f"invoice_{bid}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("6ixNine9 Motorsport Invoice", styles["Title"]),
        Spacer(1, 10),
        Paragraph(f"Booking ID: {bid}", styles["Normal"]),
        Paragraph(f"Name: {name}", styles["Normal"]),
        Paragraph(f"Phone: {phone}", styles["Normal"]),
        Paragraph(f"Plate: {plate}", styles["Normal"]),
        Paragraph(f"Date: {date}", styles["Normal"]),
        Spacer(1, 10),
        Paragraph(f"TOTAL: RM {total}", styles["Title"])
    ]

    doc.build(content)
    os.startfile(filename)
    return filename

# ================= CALENDAR =================
def pick_date():
    top = ctk.CTkToplevel(app)
    top.title("Select Date")
    top.geometry("350x300")

    cal = DateEntry(top)
    cal.pack(pady=20)

    warn = ctk.CTkLabel(top, text="", text_color="red")
    warn.pack()

    def confirm():
        d = str(cal.get_date())

        if d in BLOCKED_DATES:
            warn.configure(text="Blocked date")
            return

        if count_bookings(d) >= MAX_BOOKINGS_PER_DAY:
            warn.configure(text="Fully booked")
            return

        date_entry.configure(state="normal")
        date_entry.delete(0, "end")
        date_entry.insert(0, d)
        date_entry.configure(state="readonly")

        update_summary()
        top.destroy()

    ctk.CTkButton(top, text="CONFIRM", command=confirm).pack()

# ================= SUMMARY =================
def update_summary():
    summary.configure(state="normal")
    summary.delete("1.0", "end")

    extras = [k for k, v in extra_state.items() if v]

    summary.insert("end", "6ixNine9 Motorsport\n\n")
    summary.insert("end", f"Name: {name_entry.get()}\n")
    summary.insert("end", f"Phone: {phone_entry.get()}\n")
    summary.insert("end", f"Plate: {plate_entry.get()}\n")
    summary.insert("end", f"Date: {date_entry.get()}\n\n")

    summary.insert("end", f"Car: {car_var.get()}\n")
    summary.insert("end", f"Wrap: {wrap_var.get()}\n")
    summary.insert("end", f"Wash: {wash_var.get()}\n")
    summary.insert("end", f"Extras: {', '.join(extras)}\n")

    summary.insert("end", f"\nTOTAL: RM {grand_total()}")

    summary.configure(state="disabled")

# ================= CHECKOUT =================
def checkout():
    name = name_entry.get()
    phone = phone_entry.get()
    plate = plate_entry.get()
    date = date_entry.get()

    if not name or not phone or not plate:
        messagebox.showerror("Error", "Fill all fields")
        return

    if count_bookings(date) >= MAX_BOOKINGS_PER_DAY:
        messagebox.showerror("Full", "Date fully booked")
        return

    bid = booking_id()
    extras = [k for k, v in extra_state.items() if v]

    # 🔥 FIXED SQL (NO MORE ERROR)
    cur.execute("""
    INSERT INTO orders(
        booking_id, customer_name, phone, car_plate,
        appointment_date, car_type, color, wrap_type,
        extras, wash_package, total, status, created_at
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        bid,
        name,
        phone,
        plate,
        date,
        car_var.get(),
        color_var.get(),
        wrap_var.get(),
        ",".join(extras),
        wash_var.get(),
        grand_total(),
        "pending",
        datetime.now().isoformat()
    ))
    conn.commit()

    # PDF
    generate_pdf(bid, name, phone, plate, date, grand_total())

    # TELEGRAM ALERT
    telegram(
        f"🦈 NEW BOOKING\n\n"
        f"ID: {bid}\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Plate: {plate}\n"
        f"Date: {date}\n\n"
        f"Car: {car_var.get()}\n"
        f"Color: {color_var.get()}\n"
        f"Wrap: {wrap_var.get()}\n"
        f"Wash: {wash_var.get()}\n"
        f"Extras: {', '.join(extras) if extras else 'None'}\n\n"
        f"TOTAL: RM {grand_total()}"
    )

    messagebox.showinfo("Success", f"Booked!\n{bid}")

    update_summary()

# ================= UI =================
header = ctk.CTkFrame(app)
header.pack(fill="x", padx=10, pady=10)

ctk.CTkLabel(header, text="6ixNine9 Motorsport", font=("Arial", 24, "bold")).pack()

cust = ctk.CTkFrame(app)
cust.pack(fill="x", padx=10, pady=5)

name_entry = ctk.CTkEntry(cust, placeholder_text="Name")
name_entry.pack(side="left", expand=True, fill="x", padx=5)

phone_entry = ctk.CTkEntry(cust, placeholder_text="Phone")
phone_entry.pack(side="left", expand=True, fill="x", padx=5)

plate_entry = ctk.CTkEntry(cust, placeholder_text="Car Plate")
plate_entry.pack(side="left", expand=True, fill="x", padx=5)

date_frame = ctk.CTkFrame(app)
date_frame.pack(pady=10)

date_entry = ctk.CTkEntry(date_frame, state="readonly", width=200)
date_entry.pack(side="left")

ctk.CTkButton(date_frame, text="Pick Date", command=pick_date).pack(side="left")

body = ctk.CTkFrame(app)
body.pack(fill="both", expand=True, padx=10, pady=10)

left = ctk.CTkFrame(body)
left.pack(side="left", fill="both", expand=True, padx=5)

right = ctk.CTkFrame(body)
right.pack(side="left", fill="both", expand=True, padx=5)

ctk.CTkLabel(left, text="Car Type").pack()
ctk.CTkComboBox(left, values=list(CAR_TYPES),
                variable=car_var,
                command=lambda x: update_summary(),
                state="readonly").pack(fill="x")

ctk.CTkLabel(left, text="Color").pack()
ctk.CTkComboBox(left, values=list(COLORS),
                variable=color_var,
                command=lambda x: update_summary(),
                state="readonly").pack(fill="x")

ctk.CTkLabel(left, text="Wrap Type").pack()
ctk.CTkComboBox(left, values=list(WRAP_TYPES),
                variable=wrap_var,
                command=lambda x: update_summary(),
                state="readonly").pack(fill="x")

ctk.CTkLabel(right, text="Wash Type").pack()
ctk.CTkComboBox(right, values=list(WASH),
                variable=wash_var,
                command=lambda x: update_summary(),
                state="readonly").pack(fill="x")

ctk.CTkLabel(right, text="Extras").pack()

for k, v in EXTRAS.items():
    btn = ctk.CTkButton(right, text=f"{k} RM{v}",
                         fg_color="#2b2b2b")
    btn.configure(command=lambda b=btn, key=k: toggle_extra(key, b))
    btn.pack(fill="x", pady=3)

summary = ctk.CTkTextbox(app, height=200)
summary.pack(fill="x", padx=10, pady=10)

ctk.CTkButton(app, text="Checkout", command=checkout).pack(pady=10)

update_summary()
app.mainloop()