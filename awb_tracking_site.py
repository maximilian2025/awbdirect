from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Definim modelul utilizatorului
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Lista firmelor de curierat din România
couriers = {
    "FAN Courier": "https://api.fancourier.ro/awb-status",
    "Cargus": "https://api.cargus.ro/tracking",
    "DPD": "https://api.dpd.ro/status",
    "Sameday": "https://api.sameday.ro/tracking",
    "GLS": "https://api.gls.ro/track",
    "Fedex": "https://api.fedex.com/track",
    "Dragon Star": "https://api.dragonstar.ro/tracking",
    "Posta Romana": "https://api.posta-romana.ro/awb",
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_awb():
    awb_number = request.form['awb']
    results = {}

    for courier, api_url in couriers.items():
        response = requests.get(api_url, params={"awb": awb_number})
        if response.status_code == 200:
            results[courier] = response.json()

    return jsonify(results)

@app.route('/track-international', methods=['POST'])
def track_awb_international():
    awb_number = request.form['awb_international']
    api_url = f"https://api.17track.net/restful/track?numbers={awb_number}"
    headers = {"Accept": "application/json", "Authorization": "API_KEY_HERE"} # Înlocuiește cu cheia API reală
    
    response = requests.get(api_url, headers=headers)
    return jsonify(response.json()) if response.status_code == 200 else jsonify({"error": "AWB internațional indisponibil."})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('index'))
        return "Login eșuat! Verifică datele introduse."

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
