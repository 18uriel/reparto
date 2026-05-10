from flask import Flask, render_template, request, jsonify
import mysql.connector
import requests
import os

app = Flask(__name__)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME",     "railway"),
}

APIPERU_TOKEN = os.getenv("APIPERU_TOKEN", "")

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/consultar_dni/<dni>")
def consultar_dni(dni):
    if not dni.isdigit() or len(dni) != 8:
        return jsonify({"error": "DNI inválido"}), 400

    # 1. Buscar en BD primero
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM beneficiarios WHERE dni = %s", (dni,))
        row = cur.fetchone()
        cur.close(); db.close()
        if row:
            return jsonify({
                "dni":          row["dni"],
                "nombres":      row["nombres"],
                "apellidos":    row["apellidos"],
                "ya_recibio":   row["ya_recibio"] == 1,
                "fecha_entrega": str(row["fecha_entrega"]) if row["fecha_entrega"] else None,
                "fuente":       "base_de_datos"
            })
    except Exception as e:
        return jsonify({"error": f"Error BD: {str(e)}"}), 500

    # 2. Consultar RENIEC via apiperu.dev
    try:
        resp = requests.get(
            f"https://apiperu.dev/api/dni/{dni}",
            headers={
                "Authorization": f"Bearer {APIPERU_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=8
        )
        print("RENIEC status:", resp.status_code)
        print("RENIEC response:", resp.text)
        
        if resp.status_code == 200:
            data = resp.json()
            # apiperu.dev devuelve los datos dentro de "data"
            info = data.get("data", data)
            nombres   = info.get("nombres", "") or info.get("nombre", "")
            ap_pat    = info.get("apellido_paterno", "") or info.get("apellidoPaterno", "")
            ap_mat    = info.get("apellido_materno", "") or info.get("apellidoMaterno", "")
            apellidos = f"{ap_pat} {ap_mat}".strip()
            return jsonify({
                "dni":          dni,
                "nombres":      nombres,
                "apellidos":    apellidos,
                "ya_recibio":   False,
                "fecha_entrega": None,
                "fuente":       "reniec"
            })
    except Exception as e:
        print("Error RENIEC:", e)

    return jsonify({"error": "DNI no encontrado. Ingresa el nombre manualmente."}), 404

@app.route("/api/registrar", methods=["POST"])
def registrar():
    data      = request.json
    dni       = (data.get("dni") or "").strip()
    nombres   = (data.get("nombres") or "").strip().upper()
    apellidos = (data.get("apellidos") or "").strip().upper()

    if not dni.isdigit() or len(dni) != 8:
        return jsonify({"ok": False, "error": "DNI inválido"}), 400
    if not nombres:
        return jsonify({"ok": False, "error": "Ingresa los nombres"}), 400

    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT ya_recibio, nombres, apellidos FROM beneficiarios WHERE dni = %s", (dni,))
        row = cur.fetchone()

        if row:
            if row["ya_recibio"]:
                cur.close(); db.close()
                return jsonify({
                    "ok": False,
                    "error": f"⚠ {row['nombres']} {row['apellidos']} YA RECIBIÓ su regalo.",
                    "duplicado": True
                })
            cur.execute(
                "UPDATE beneficiarios SET ya_recibio=1, fecha_entrega=NOW(), nombres=%s, apellidos=%s WHERE dni=%s",
                (nombres, apellidos, dni)
            )
        else:
            cur.execute(
                "INSERT INTO beneficiarios (dni, nombres, apellidos, ya_recibio, fecha_entrega) VALUES (%s,%s,%s,1,NOW())",
                (dni, nombres, apellidos)
            )

        db.commit()
        cur.close(); db.close()
        return jsonify({"ok": True, "mensaje": f"✓ Regalo entregado a {nombres} {apellidos}"})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/lista")
def lista():
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT dni, nombres, apellidos, ya_recibio,
                   DATE_FORMAT(fecha_entrega, '%d/%m/%Y %H:%i') as fecha_entrega
            FROM beneficiarios ORDER BY fecha_entrega DESC
        """)
        rows = cur.fetchall()
        cur.close(); db.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def stats():
    try:
        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("""
            SELECT COUNT(*) as total, SUM(ya_recibio) as entregados,
                   COUNT(*) - SUM(ya_recibio) as pendientes
            FROM beneficiarios
        """)
        row = cur.fetchone()
        cur.close(); db.close()
        return jsonify(row)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)))
