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

    try:from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
import os
import random
import requests

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


app = Flask(__name__)


# ---------------- TELEGRAM ----------------

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"


def telegram(msg):

    try:

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg
            }
        )

    except:

        pass




# ---------------- CONFIG ----------------


CAR_TYPES = {

    "Sedan": 2000,

    "MPV": 2300

}



BRAND = {

    "KTN": 500,

    "NAKA FILM PET": 1000,

    "No":0

}




WASH = {


    "Small": {

        "price":50,

        "desc":
        "Exterior wash, drying, tyre shine"

    },


    "Medium": {

        "price":100,

        "desc":
        "Exterior wash, vacuum, dashboard cleaning"

    },


    "Large": {

        "price":180,

        "desc":
        "Full wash, interior detailing, polish"

    },


    "Large Plus": {

        "price":300,

        "desc":
        "Full detail, paint protection, leather treatment"

    }

}





COLORS = {

    "Black":0,

    "White":0,

    "Red":100,

    "Blue":100

}





BLOCKED_DATES = {

    "2026-01-01",

    "2026-02-10"

}



MAX_BOOKINGS_PER_DAY = 5





# ---------------- DATABASE ----------------


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





# ---------------- HELPERS ----------------


def count_bookings(date):

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE appointment_date=?",
        (date,)
    )

    return cur.fetchone()[0]






def calculate_total(car,color,brand,wash):


    total = 0


    total += CAR_TYPES.get(car,0)


    total += COLORS.get(color,0)


    total += BRAND.get(brand,0)


    total += WASH.get(wash,{}).get(
        "price",
        0
    )


    return total





def generate_booking_id():

    return (

        f"MS-"
        f"{datetime.now().strftime('%Y%m%d')}-"
        f"{random.randint(1000,9999)}"

    )







# ---------------- PDF ----------------


def generate_pdf(

    booking_id,
    name,
    phone,
    plate,
    date,
    car,
    color,
    brand,
    wash,
    total

):


    folder = os.path.join(

        BASE_DIR,

        "static",

        "invoices_private"

    )


    os.makedirs(
        folder,
        exist_ok=True
    )



    file_path = os.path.join(

        folder,

        f"{booking_id}.pdf"

    )



    doc = SimpleDocTemplate(

        file_path,

        pagesize=A4

    )


    styles = getSampleStyleSheet()



    content = [


        Paragraph(

        "🦈 6ixNine9 Motorsport Receipt",

        styles["Title"]

        ),


        Spacer(1,12),


        Paragraph(
        f"Booking ID: {booking_id}",
        styles["Normal"]
        ),


        Paragraph(
        f"Name: {name}",
        styles["Normal"]
        ),


        Paragraph(
        f"Phone: {phone}",
        styles["Normal"]
        ),


        Paragraph(
        f"Plate: {plate}",
        styles["Normal"]
        ),


        Paragraph(
        f"Date: {date}",
        styles["Normal"]
        ),



        Spacer(1,12),



        Paragraph(
        f"Car: {car}",
        styles["Normal"]
        ),


        Paragraph(
        f"Brand: {brand}",
        styles["Normal"]
        ),


        Paragraph(
        f"Colour: {color}",
        styles["Normal"]
        ),



        Paragraph(
        f"Package: {wash}",
        styles["Normal"]
        ),


        Paragraph(
        f"Package Details: {WASH[wash]['desc']}",
        styles["Normal"]
        ),



        Spacer(1,12),



        Paragraph(

        f"TOTAL: RM {total}",

        styles["Title"]

        )

    ]



    doc.build(content)



    return (

        f"/static/invoices_private/"
        f"{booking_id}.pdf"

    )








# ---------------- ROUTES ----------------


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


    name = request.form["name"]


    phone = request.form["phone"]


    plate = request.form["plate"]


    date = request.form["date"]



    car = request.form["car"]


    color = request.form["color"]


    brand = request.form["brand"]


    wash = request.form["wash"]






    if date in BLOCKED_DATES:


        return "❌ Date blocked"





    if count_bookings(date) >= MAX_BOOKINGS_PER_DAY:


        return "❌ Fully booked"






    total = calculate_total(

        car,

        color,

        brand,

        wash

    )



    booking_id = generate_booking_id()





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

    VALUES(?,?,?,?,?,?,?,?,?,?,?)

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







    pdf_url = generate_pdf(

        booking_id,

        name,

        phone,

        plate,

        date,

        car,

        color,

        brand,

        wash,

        total

    )







    telegram(f"""

🦈 NEW BOOKING


ID: {booking_id}
Name: {name}
Phone: {phone}
Plate: {plate}
Car: {car}
Brand: {brand}
Package: {wash}
TOTAL: RM {total}

""")







    return f"""


<h2>✔ Booking Successful</h2>


<p>ID: {booking_id}</p>


<a href="{pdf_url}" download>

📄 Download Invoice PDF

</a>


<br><br>


<a href="/">

Back Home

</a>


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

    "No":0,
    
    "Interior Pro A - Small":240,

    "Interior Pro B - Large":550,

    "Interior Pro C - Large plus":900

}



COLORS = {

    "No":0,

    "Black":0,

    "White":0,

    "Red":0,

    "Blue":0

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
