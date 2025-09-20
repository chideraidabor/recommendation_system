from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)

@bp.route("/recommendations")
def get_recommendations():
    return jsonify({"message": "placeholder"})


@bp.route("/")
def status():
    return jsonify({"status": "ok"})