from flask import Flask, render_template, request, redirect, url_for, session
import pigpio
import time, json, threading
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key'
PASSWORD = 'Hsbc1930'
SCHEDULE_FILE = 'schedule.json'

pi = pigpio.pi()
RELAY_PIN = 17
pi.set_mode(RELAY_PIN, pigpio.OUTPUT)
pi.write(RELAY_PIN, 1)  # OFF

def load_schedule():
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_schedule(schedule):
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(schedule, f)

def ring_bell(duration=1):
    pi.write(RELAY_PIN, 0)  # ON
    time.sleep(duration)
    pi.write(RELAY_PIN, 1)  # OFF

def check_schedule():
    while True:
        now = datetime.now().strftime("%H:%M")
        schedule = load_schedule()
        if now in schedule:
            ring_bell()
            time.sleep(60)
        time.sleep(1)

threading.Thread(target=check_schedule, daemon=True).start()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("logged_in"):
            return f(*args, **kwargs)
        return redirect(url_for("login"))
    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", schedule=load_schedule())

@app.route("/add_time", methods=["POST"])
@login_required
def add_time():
    time_entry = request.form["time"]
    schedule = load_schedule()
    if time_entry not in schedule:
        schedule.append(time_entry)
        save_schedule(sorted(schedule))
    return redirect(url_for("dashboard"))

@app.route("/delete_time", methods=["POST"])
@login_required
def delete_time():
    time_entry = request.form["time"]
    schedule = load_schedule()
    if time_entry in schedule:
        schedule.remove(time_entry)
        save_schedule(schedule)
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
