from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

GOAL = 2239
CRUISE_DATE = date(2026, 10, 24)

def init_db():
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            note TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()

    c.execute("SELECT amount, note, date FROM savings ORDER BY id ASC")
    entries = c.fetchall()

    c.execute("SELECT SUM(amount) FROM savings")
    total = c.fetchone()[0]
    if total is None:
        total = 0

    conn.close()

    progress = (total / GOAL) * 100 if GOAL else 0

    days_left = (CRUISE_DATE - date.today()).days

    # graph data
    labels = []
    values = []
    running = 0

    for e in entries:
        running += e[0]
        labels.append(e[2])
        values.append(running)

    return render_template(
        "index.html",
        total=total,
        goal=GOAL,
        progress=progress,
        entries=entries,
        days_left=days_left,
        labels=labels,
        values=values
    )

@app.route("/add", methods=["POST"])
def add():
    amount = float(request.form["amount"])
    note = request.form["note"]
    date_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO savings (amount, note, date) VALUES (?, ?, ?)",
        (amount, note, date_str)
    )
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
