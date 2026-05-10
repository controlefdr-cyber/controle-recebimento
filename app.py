from flask import Flask, render_template, request, jsonify
import sqlite3, os

app = Flask(__name__)
DB = "recebimentos.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recebimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT NOT NULL,
            data TEXT NOT NULL,
            nf TEXT NOT NULL,
            doca TEXT NOT NULL,
            inicio TEXT DEFAULT '',
            termino TEXT DEFAULT '',
            status TEXT DEFAULT 'Aguardando'
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/recebimentos", methods=["GET"])
def listar():
    conn = get_db()
    rows = conn.execute("SELECT * FROM recebimentos ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/recebimentos", methods=["POST"])
def criar():
    d = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO recebimentos (placa, data, nf, doca) VALUES (?,?,?,?)",
        (d["placa"], d["data"], d["nf"], d["doca"])
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/recebimentos/<int:rid>", methods=["PUT"])
def editar(rid):
    d = request.json
    conn = get_db()
    conn.execute(
        "UPDATE recebimentos SET placa=?, data=?, nf=?, doca=?, inicio=?, termino=?, status=? WHERE id=?",
        (d["placa"], d["data"], d["nf"], d["doca"], d.get("inicio",""), d.get("termino",""), d.get("status","Aguardando"), rid)
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/recebimentos/<int:rid>", methods=["DELETE"])
def remover(rid):
    conn = get_db()
    conn.execute("DELETE FROM recebimentos WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/iniciar/<int:rid>", methods=["POST"])
def iniciar(rid):
    from datetime import datetime
    hora = datetime.now().strftime("%H:%M")
    conn = get_db()
    conn.execute("UPDATE recebimentos SET inicio=?, status='Em andamento' WHERE id=?", (hora, rid))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "hora": hora})

@app.route("/api/finalizar/<int:rid>", methods=["POST"])
def finalizar(rid):
    from datetime import datetime
    hora = datetime.now().strftime("%H:%M")
    conn = get_db()
    conn.execute("UPDATE recebimentos SET termino=?, status='Concluído' WHERE id=?", (hora, rid))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "hora": hora})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

init_db()
