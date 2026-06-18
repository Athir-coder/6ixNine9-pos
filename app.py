from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import os
import random
import requests


app = Flask(__name__)


# TELEGRAM

BOT_TOKEN = "8716076962:AAHpIFuyq7Jq51Gy4Dj9PsPexClS-v04-Oo"
CHAT_ID = "723175483"


def telegram(msg):

    try:

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id":CHAT_ID,
                "text":msg
            }
        )

    except:
        pass



# PRICE

CAR_TYPES = {

    "No":0,
    
    "Sedan":2000,

    "MPV":2300

}



BRAND = {

    "No":0,

    "NAKA FILM PET":1000,

    "KTN":500

}



WASH = {

    "Interior Pro A - Small":240,

    "Interior Pro B - Large":550,

    "Interior Pro C - Large plus":900

}



COLORS = {

    "Black":0,

    "White":0,

    "Red":100,

    "Blue":100

}



BLOCKED_DATES = {

"2026-01-01"

}



MAX_BOOKINGS_PER_DAY = 5




# DATABASE


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(
    BASE_DIR,
    "orders.db"
)



conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)


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

brand TEXT,

wash_type TEXT,

total REAL,

created_at TEXT

)
""")


conn.commit()




def count_bookings(date):

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE appointment_date=?",
        (date,)
    )

    return cur.fetchone()[0]






def calculate_total(
        car,
        color,
        brand,
        wash
):


    total = 0


    # wrap price

    if brand != "No Wrap":

        total += CAR_TYPES.get(car,0)

        total += BRAND.get(brand,0)



    # wash only

    total += WASH.get(wash,0)



    total += COLORS.get(color,0)


    return total





def generate_id():

    return (

    "MS-"

    + datetime.now().strftime("%Y%m%d")

    + "-"

    + str(random.randint(1000,9999))

    )






@app.route("/")

def home():


    return render_template(

        "index.html",

        cars=CAR_TYPES,

        brand=BRAND,

        colors=COLORS,

        washes=WASH

    )







@app.route("/book",methods=["POST"])

def book():


    name=request.form["name"]

    phone=request.form["phone"]

    plate=request.form["plate"]

    date=request.form["date"]


    car=request.form["car"]

    color=request.form["color"]

    brand=request.form["brand"]

    wash=request.form["wash"]



    if date in BLOCKED_DATES:

        return "Date blocked"



    if count_bookings(date)>=MAX_BOOKINGS_PER_DAY:

        return "Fully booked"




    total = calculate_total(

        car,

        color,

        brand,

        wash

    )



    booking_id = generate_id()




    cur.execute("""

    INSERT INTO orders(

    booking_id,

    name,

    phone,

    plate,

    appointment_date,

    car_type,

    color,

    brand,

    wash_type,

    total,

    created_at


    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    booking_id,

    name,

    phone,

    plate,

    date,

    car,

    color,

    brand,

    wash,

    total,

    datetime.now().isoformat()

    ))



    conn.commit()




    telegram(f"""

🦈 NEW BOOKING


ID: {booking_id}


Name:
{name}


Phone:
{phone}


Plate:
{plate}


Car:
{car}


Brand:
{brand}


Color:
{color}


Wash:
{wash}


TOTAL:
RM {total}


""")


    return f"""

<h1>Booking Successful</h1>

<p>ID: {booking_id}</p>

<p>Total RM {total}</p>

<a href="/">Back</a>


"""







if __name__=="__main__":


    port=int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
