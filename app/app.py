import glob
import json
import os
from datetime import datetime, timezone

from flask import Flask, jsonify

ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", "artifacts")

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "service": "daily-rates-api",
        "endpoints": {
            "/health": "Service status",
            "/latest-report": "Most recent exchange rate report",
        },
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/latest-report")
def latest_report():
    files = sorted(glob.glob(os.path.join(ARTIFACTS_DIR, "report_*.json")))
    if not files:
        return jsonify({"error": "No reports found"}), 404

    try:
        with open(files[-1]) as f:
            return jsonify(json.load(f))
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Failed to read report %s", files[-1])
        return jsonify({"error": "Report could not be read"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
