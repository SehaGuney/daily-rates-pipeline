from flask import Flask, jsonify
import glob, json

app = Flask(__name__)

@app.route("/latest-report")
def latest_report():
    files = sorted(glob.glob("artifacts/report_*.json"))
    if not files:
        return jsonify({"error":"no reports"}), 404
    with open(files[-1]) as f:
        data = json.load(f)
    return jsonify(data)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
