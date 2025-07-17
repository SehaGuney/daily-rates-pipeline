from flask import Flask, jsonify
import glob, json
import os
from datetime import datetime

app = Flask(__name__)

# Ana sayfa route'u ekleyin
@app.route("/")
def home():
    return jsonify({
        "message": "Döviz Uygulaması Çalışıyor!",
        "endpoints": [
            "/latest-report - En son raporu gösterir",
            "/health - Sistem durumu"
        ],
        "timestamp": datetime.now().isoformat()
    })

# Sistem durumu için health check
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/latest-report")
def latest_report():
    # Artifacts klasörünü kontrol et
    if not os.path.exists("artifacts"):
        return jsonify({
            "error": "artifacts klasörü bulunamadı",
            "message": "Henüz rapor oluşturulmamış"
        }), 404
    
    files = sorted(glob.glob("artifacts/report_*.json"))
    if not files:
        return jsonify({
            "error": "no reports",
            "message": "artifacts klasöründe rapor dosyası bulunamadı"
        }), 404
    
    try:
        with open(files[-1]) as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": "Rapor okunamadı",
            "details": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
