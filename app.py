from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = "phishguard_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
os.makedirs(DATABASE_FOLDER, exist_ok=True)

DATABASE = os.path.join(DATABASE_FOLDER, "phishing.db")
# ===========================
# DATABASE FUNCTIONS
# ===========================

def get_connection():
    return sqlite3.connect(DATABASE)


def create_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            site TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


create_database()
# ===========================
# SAMPLE PHISHING EMAILS
# ===========================

emails = [
    {
        "subject": "Microsoft Security Alert",
        "sender": "security@microsoft-login.com",
        "site": "Microsoft",
        "message": "We detected unusual login activity. Verify your account immediately."
    },
    {
        "subject": "Amazon Order Suspended",
        "sender": "orders@amazon-alert.com",
        "site": "Amazon",
        "message": "Your recent order is on hold. Please verify your identity."
    },
    {
        "subject": "Google Password Expired",
        "sender": "support@gmail-security.com",
        "site": "Google",
        "message": "Your Google password expires today. Login to continue."
    },
    {
        "subject": "Netflix Subscription Failed",
        "sender": "billing@netflix-help.com",
        "site": "Netflix",
        "message": "Payment failed. Update your payment details."
    },
    {
        "subject": "Bank Account Locked",
        "sender": "security@bank-alert.com",
        "site": "Bank",
        "message": "Your bank account has been temporarily locked."
    }
]
# ===========================
# HOME PAGE
# ===========================

@app.route("/")
def index():
    return render_template("index.html", emails=emails)
# ===========================
# FAKE LOGIN PAGE
# ===========================

@app.route("/login/<site>")
def login(site):
    return render_template("fake_login.html", site=site)
# ===========================
# LOGIN SUBMISSION
# ===========================

@app.route("/submit", methods=["POST"])
def submit():

    username = request.form.get("username")
    site = request.form.get("site")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interactions
        (username, action, site, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            "Submitted (Simulation)",
            site,
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()

    flash(
        "⚠️ This was a phishing awareness simulation. Never enter your credentials on suspicious websites!",
        "warning"
    )

    return redirect(url_for("awareness"))
# ===========================
# AWARENESS PAGE
# ===========================

@app.route("/awareness")
def awareness():
    return render_template("awareness.html")
# ===========================
# REPORT PAGE
# ===========================

@app.route("/report")
def report():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM interactions
        ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "report.html",
        data=data
    )
# ===========================
# RESET DATABASE
# ===========================

@app.route("/reset")
def reset():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interactions")

    conn.commit()
    conn.close()

    flash("Database cleared successfully.", "success")

    return redirect(url_for("report"))
@app.route("/about")
def about():
    return render_template("about.html")
# ===========================
# RUN APPLICATION
# ===========================

if __name__ == "__main__":
    app.run(debug=True)