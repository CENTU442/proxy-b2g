import os
import requests
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)

# Habilitar CORS completo para cualquier origen y permitir el header 'ticket'
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "ticket", "Authorization", "Accept"],
    methods=["GET", "OPTIONS"]
)

# URL oficial vigente de la API Compra Ágil v2 de ChileCompra (Mayo 2026)
CHILECOMPRA_V2_BASE = "https://api2.mercadopublico.cl/v2/compra-agil"

# Ticket por defecto (se recomienda configurarlo también como variable de entorno MP_TICKET en Render)
DEFAULT_TICKET = os.environ.get("MP_TICKET", "7C185840-60FA-4EF0-AE7A-DF87F5336FE6")

# Parámetros oficiales aceptados por /v2/compra-agil
ALLOWED_QUERY_PARAMS = {
    "ttl_cambio_ms",
    "cambio_desde",
    "cambio_hasta",
    "publicado_desde",
    "publicado_hasta",
    "estado",
    "region",
    "id",
    "q",
    "tamano_pagina",
    "numero_pagina",
    "ordenar_por",
}


def resolve_ticket():
    """Obtiene el ticket desde el header HTTP, query string o variable de entorno."""
    return (
        request.headers.get("ticket")
        or request.args.get("ticket")
        or DEFAULT_TICKET
    ).strip()


def forward_to_chilecompra(url, params=None):
    """Reenvía la consulta a api2.mercadopublico.cl usando autenticación por Header 'ticket'."""
    ticket = resolve_ticket()
    headers = {
        "ticket": ticket,
        "Accept": "application/json",
        "User-Agent": "B2G-Chile-Proxy/2.0",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=25)
        try:
            payload = resp.json()
        except ValueError:
            payload = {
                "success": "NOK",
                "message": f"Respuesta no JSON desde ChileCompra (HTTP {resp.status_code})",
                "raw": resp.text[:500],
            }
        # Devolvemos el código real (200, 401, 429, etc.) para diagnóstico transparente
        return jsonify(payload), resp.status_code
    except requests.Timeout:
        return jsonify({
            "success": "NOK",
            "message": "Tiempo de espera agotado al consultar api2.mercadopublico.cl",
        }), 504
    except Exception as exc:
        return jsonify({
            "success": "NOK",
            "message": f"Error de conexión hacia ChileCompra: {str(exc)}",
        }), 502


@app.route("/")
def home():
    """Página de estado con enlaces de prueba en vivo."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Proxy API Compra Ágil v2 - Activo</title>
        <style>
            body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; padding: 40px 16px; }
            .card { background: #1e293b; border: 1px solid #334155; padding: 28px; border-radius: 16px; max-width: 640px; width: 100%; }
            h1 { color: #10b981; margin-top: 0; font-size: 22px; }
            a { color: #38bdf8; text-decoration: none; font-family: monospace; }
            a:hover { text-decoration: underline; }
            .box { background: #0f172a; padding: 12px; border-radius: 10px; margin: 10px 0; border: 1px solid #334155; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Proxy API Compra Ágil v2 Activo</h1>
            <p>Conectado al endpoint oficial <code>https://api2.mercadopublico.cl/v2/compra-agil</code> usando autenticación por header <code>ticket</code>.</p>
            <div class="box">
                <strong>Probar Maule (Región 7) en vivo:</strong><br>
                <a href="/api/compra-agil?estado=publicada&region=7&tamano_pagina=15" target="_blank">
                    /api/compra-agil?estado=publicada&amp;region=7&amp;tamano_pagina=15
                </a>
            </div>
            <div class="box">
                <strong>Probar Arica (Región 15) en vivo:</strong><br>
                <a href="/api/compra-agil?estado=publicada&region=15&tamano_pagina=15" target="_blank">
                    /api/compra-agil?estado=publicada&amp;region=15&amp;tamano_pagina=15
                </a>
            </div>
        </div>
    </body>
    </html>
    """)
