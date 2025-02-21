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
    first_digit = awb[0]  # Prima cifră a AWB
    for courier, prefixes in couriers.items():
        if first_digit in prefixes:
            return courier
    return "Curier necunoscut"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track', methods=['POST'])
def track_awb():
    awb_number = request.form.get('awb', '').strip()
    if not awb_number:
        return jsonify({"error": "Introduceți un număr AWB!"})

    courier = identify_courier(awb_number)
    if courier == "Curier necunoscut":
        return jsonify({"error": "AWB necunoscut sau curier indisponibil."})

    tracking_info = fetch_tracking_info(courier, awb_number)
    return jsonify({"courier": courier, "tracking_info": tracking_info})

def fetch_tracking_info(courier, awb):
    """Funcție pentru interogarea API-urilor curierilor"""
    api_endpoints = {
        "FAN Courier": "https://api.fancourier.ro/awb-status",
        "Cargus": "https://api.cargus.ro/tracking",
        "DPD": "https://api.dpd.ro/status",
        "SameDay": "https://api.sameday.ro/tracking",
        "GLS": "https://api.gls.ro/track",
    }

    if courier in api_endpoints:
        try:
            print(f"🔍 Trimit cerere către {api_endpoints[courier]} cu AWB {awb}")  # Debug
            response = requests.get(api_endpoints[courier], params={"awb": awb}, timeout=5)
            print(f"📩 Răspuns: {response.status_code}, {response.text}")  # Debug

            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "Eroare API", "location": "N/A"}
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Eroare conexiune: {e}")  # Debug
            return {"status": "Eroare conexiune API", "location": "N/A"}

    return {"status": "Informație indisponibilă", "location": "N/A"}

if __name__ == '__main__':
    app.run(debug=True)
