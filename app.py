from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import sqlite3

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend"
)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/recommendations/<item_id>", methods=["GET"])
def get_recommendations(item_id):
    conn = sqlite3.connect("Database/recommendation.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recommended_item, cosine_similarity
        FROM recommendations
        WHERE item_id = ?
        ORDER BY cosine_similarity DESC
        LIMIT 5
    """, (item_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"recommended_item": r[0], "score": r[1]} for r in rows])


@app.route("/items", methods=["GET"])
def get_items():
    conn = sqlite3.connect("Database/recommendation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT item_id, item_description, unit_price FROM Items")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"item_id": r[0], "item_description":r[1], "unit_price":r[2]} for r in rows])


if __name__ == "__main__":
    app.run(debug=True)
