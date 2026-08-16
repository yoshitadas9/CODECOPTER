from fastapi import FastAPI
import sqlite3

app = FastAPI()


# ---------------- DATABASE ----------------

def get_db():
    return sqlite3.connect("codecopter.db")


# Create database tables
def create_database():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drones (
            id INTEGER PRIMARY KEY,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine TEXT,
            destination TEXT,
            drone_id INTEGER,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drone_id INTEGER,
            temperature REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drone_id INTEGER,
            message TEXT
        )
    """)

    # Add some drones if database is empty
    cursor.execute("SELECT COUNT(*) FROM drones")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO drones (id, status) VALUES (?, ?)",
            (1, "available")
        )

        cursor.execute(
            "INSERT INTO drones (id, status) VALUES (?, ?)",
            (2, "delivering")
        )

    db.commit()
    db.close()


create_database()


# ---------------- HOME ----------------

@app.get("/")
def home():

    return {
        "message": "CODECOPTER backend is running!"
    }


# ---------------- DRONES ----------------

@app.get("/drones")
def get_drones():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, status FROM drones")

    drones = cursor.fetchall()

    db.close()

    result = []

    for drone in drones:

        result.append({
            "id": drone[0],
            "status": drone[1]
        })

    return {
        "drones": result
    }


# ---------------- DELIVERIES ----------------

@app.post("/deliveries")
def create_delivery(
    medicine: str,
    destination: str,
    drone_id: int
):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO deliveries
        (medicine, destination, drone_id, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            medicine,
            destination,
            drone_id,
            "created"
        )
    )

    db.commit()

    delivery_id = cursor.lastrowid

    db.close()

    return {
        "message": "Delivery created",
        "delivery_id": delivery_id,
        "medicine": medicine,
        "destination": destination,
        "drone_id": drone_id,
        "status": "created"
    }


# ---------------- VIEW DELIVERIES ----------------

@app.get("/deliveries")
def get_deliveries():

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, medicine, destination, drone_id, status
        FROM deliveries
        """
    )

    deliveries = cursor.fetchall()

    db.close()

    result = []

    for delivery in deliveries:

        result.append({
            "id": delivery[0],
            "medicine": delivery[1],
            "destination": delivery[2],
            "drone_id": delivery[3],
            "status": delivery[4]
        })

    return {
        "deliveries": result
    }


# ---------------- UPDATE DELIVERY ----------------

@app.put("/deliveries/{delivery_id}")
def update_delivery(
    delivery_id: int,
    status: str
):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE deliveries
        SET status = ?
        WHERE id = ?
        """,
        (status, delivery_id)
    )

    db.commit()

    db.close()

    return {
        "message": "Delivery status updated",
        "delivery_id": delivery_id,
        "status": status
    }


# ---------------- TEMPERATURE ----------------

@app.post("/temperature")
def receive_temperature(
    drone_id: int,
    temperature: float
):

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO temperature
        (drone_id, temperature)
        VALUES (?, ?)
        """,
        (drone_id, temperature)
    )

    # Medical supplies should stay within safe temperature
    if temperature < 2 or temperature > 8:

        message = "WARNING: Temperature outside safe range!"

        cursor.execute(
            """
            INSERT INTO alerts
            (drone_id, message)
            VALUES (?, ?)
            """,
            (drone_id, message)
        )

        db.commit()
        db.close()

        return {
            "drone_id": drone_id,
            "temperature": temperature,
            "alert": message
        }

    db.commit()
    db.close()

    return {
        "drone_id": drone_id,
        "temperature": temperature,
        "message": "Temperature is safe"
    }


# ---------------- ALERTS ----------------

@app.get("/alerts")
def get_alerts():

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, drone_id, message
        FROM alerts
        """
    )

    alerts = cursor.fetchall()

    db.close()

    result = []

    for alert in alerts:

        result.append({
            "id": alert[0],
            "drone_id": alert[1],
            "message": alert[2]
        })

    return {
        "alerts": result
    }
