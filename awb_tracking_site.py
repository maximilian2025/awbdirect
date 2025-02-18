from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Lista formatelor AWB și curierii corespunzători
couriers = {
    "FAN Courier": ["7"],
    "Cargus": ["1"],
    "DPD": ["0"],
    "SameDay": ["2"],
    "GLS": ["5"],
}

def identify_courier(awb):
    """Detectează curierul pe baza numărului AWB"""
    first_digit = awb[0]
    for courier, prefixes in couriers.items():
        if first_digit in prefixes:
            return courier
    return "Curier necunoscut"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_awb():
    awb_number = request.form['awb']
    courier = identify_courier(awb_number)
    
    if courier == "Curier necunoscut":
        return jsonify({"error": "AWB necunoscut sau curier indisponibil."})
    
    return jsonify({"courier": courier, "tracking_info": "Informație indisponibilă"})

if __name__ == '__main__':
    app.run(debug=True)
