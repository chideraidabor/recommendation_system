from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

CORS(app)

DB_PATH = "recommendation.db"
CURRENT_CONTEXT = {"part": None}

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ================================
# HEALTH CHECK
# ================================
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ================================
# RECOMMENDER UI
# ================================
@app.route("/recommender")
def recommender_ui():
    return render_template("recommender.html")


# ================================
# RECOMMENDATIONS (MIRRORS 5000)
# ================================
@app.route("/recommendations/<item_id>", methods=["GET"])
def get_recommendations(item_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT recommended_item, cosine_similarity
        FROM Recommendations
        WHERE item_id = ?
        ORDER BY cosine_similarity DESC
        LIMIT 5
    """, (item_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "recommended_item": r["recommended_item"],
            "score": r["cosine_similarity"]
        }
        for r in rows
    ]), 200

CURRENT_CONTEXT = {"part": None}

@app.route("/context", methods=["GET"])
def get_context():
    return jsonify(CURRENT_CONTEXT), 200


@app.route("/context", methods=["POST"])
def set_context():
    data = request.get_json(silent=True) or {}
    part = data.get("part")

    if not part:
        return jsonify({"error": "Missing part"}), 400

    CURRENT_CONTEXT["part"] = part
    print(f"[Context] Updated part → {part}")
    return jsonify({"ok": True, "part": part}), 200
# ================================
# ENTRY POINT
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
