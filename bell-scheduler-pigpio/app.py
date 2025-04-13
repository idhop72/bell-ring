from flask import Flask, request, redirect, render_template, session, url_for
import RPi.GPIO as GPIO
import time
from datetime import datetime
import threading

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # for session management

PASSWORD = 'Hsbc1930'
RELAY_PIN = 17  # GPIO pin connected to the relay
schedule = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

def activate_bell():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(RELAY_PIN, GPIO.LOW)

def bell_scheduler():
    while True:
        now = datetime.now().strftime('%H:%M')
        if now in schedule:
            activate_bell()
            time.sleep(60)  # wait 60 sec to avoid retriggering within the same minute
        time.sleep(1)

threading.Thread(target=bell_scheduler, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('dashboard.html', schedule=schedule)

@app.route('/add_time', methods=['POST'])
def add_time():
    if not session.get('logged_in'):
        return redirect('/')
    time_to_add = request.form['time']
    if time_to_add not in schedule:
        schedule.append(time_to_add)
    return redirect('/dashboard')

@app.route('/delete_time', methods=['POST'])
def delete_time():
    if not session.get('logged_in'):
        return redirect('/')
    time_to_delete = request.form['time']
    if time_to_delete in schedule:
        schedule.remove(time_to_delete)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        GPIO.cleanup()
