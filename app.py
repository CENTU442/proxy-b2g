import os
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TICKET = "7C185840-60FA-4EF0-AE7A-DF87F5336FE6"

@app.route('/')
def home():
    return render_template_string("""
    <html>
    <body style="background:#0f172a; color:#fff; text-align:center; padding-top:50px; font-family:Arial;">
        <h1>Servidor Proxy B2G Operativo</h1>
        <p>Conectado correctamente a Mercado Público.</p>
    </body>
    </html>
    """)

@app.route('/api/compras-agiles', methods=['GET'])
def get_compras_agiles():
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/comprasagiles.json?ticket={TICKET}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return jsonify({"status": "success", "data": response.json()})
        else:
            return jsonify({"status": "error", "message": f"Código {response.status_code}"}), 502
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)