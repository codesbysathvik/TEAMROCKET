# backend/app.py
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3, os, time
import json
from utils import extract_features, trace_redirects
from models import SmallModelFromFiles

DB_PATH = os.path.join(os.path.dirname(__file__), "scans.db")
app = Flask(__name__)
CORS(app)
ml = SmallModelFromFiles()

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        # ensure parent folder exists (should be backend/)
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

# startup() used to create DB tables. Some Flask versions removed
# `before_first_request`, so we create tables at import time inside app context.
def startup():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        timestamp INTEGER,
        heuristic_score INTEGER,
        ml_prob REAL,
        final_score INTEGER,
        signals TEXT,
        redirect_trace TEXT
    )""")
    db.execute("""
    CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        timestamp INTEGER,
        score INTEGER,
        signals TEXT
    )""")
    db.commit()

# Run startup immediately inside the application context so tables exist
# before the first request (compatible with Flask 2.x and 3.x).
with app.app_context():
    startup()

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def heuristic_score_and_signals(features: dict):
    score = 0; signals = []
    if features.get("has_ip"): score += 30; signals.append("host looks like IP")
    if features.get("has_at_symbol"): score += 25; signals.append("contains '@'")
    if features.get("uses_shortener"): score += 20; signals.append("uses shortener")
    if features.get("suspicious_word_count",0) > 0:
        cnt = features["suspicious_word_count"]; add = min(30, cnt*12)
        score += add; signals.append(f"{cnt} suspicious word(s)")
    if features.get("url_length",0) > 75: score += 10; signals.append("very long URL")
    if features.get("host_entropy",0) > 3.5: score += 8; signals.append("high host entropy")
    if features.get("is_https") == 0: score += 5; signals.append("not HTTPS")
    final = max(0, min(100, int(score)))
    return final, signals

def combine_scores(heur, ml_prob):
    if ml_prob is None: return heur
    ml_score = int(round(ml_prob*100))
    combined = int(round(0.6*heur + 0.4*ml_score))
    return max(0, min(100, combined))

@app.route("/scan", methods=["POST"])
def scan():
    data = request.get_json() or {}
    url = (data.get("url") or "").strip()
    if not url: return jsonify({"error":"no url provided"}), 400

    # extract features
    features = extract_features(url)

    # --- ML payload mapping (inserted) ---
    # prepare payload expected by ML trainer: clean_url + feature1, feature2
    # mapping choice: feature1=url_length, feature2=host_entropy
    ml_payload = {
        "url": url,
        "clean_url": url,  # replace with cleaned text if you have a cleaner
        "feature1": float(features.get("url_length", 0.0)),
        "feature2": float(features.get("host_entropy", 0.0))
    }
    # Try preferred method name first; fall back to legacy if needed
    try:
        ml_prob = ml.predict_prob(ml_payload)  # expected to return 0..1 or None
    except AttributeError:
        try:
            ml_prob = ml.predict_malicious_prob(features)
        except AttributeError:
            ml_prob = None
    # --- end ml mapping ---

    # heuristic scoring
    heur, signals = heuristic_score_and_signals(features)

    # redirect tracing (safe, with timeout and limited hops)
    redirect_trace = trace_redirects(url, max_hops=6, timeout=5.0)

    # combine ML + heuristics
    final = combine_scores(heur, ml_prob)
    advice = "High risk — do NOT click." if final>=70 else ("Medium risk — be cautious." if final>=40 else "Low risk.")

    try:
        db = get_db()
        db.execute("INSERT INTO scans (url,timestamp,heuristic_score,ml_prob,final_score,signals,redirect_trace) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (url, int(time.time()), heur, ml_prob, final, ",".join(signals), json.dumps(redirect_trace)))
        db.commit()
    except Exception as e:
        app.logger.error("DB insert failed: %s", e)

    return jsonify({
        "url":url,
        "features":features,
        "heuristic_score":heur,
        "ml_prob":ml_prob,
        "final_score":final,
        "signals":signals,
        "redirect_trace":redirect_trace,
        "advice":advice
    })
@app.route("/scan_attachment", methods=["POST"])
def scan_attachment():
    data = request.get_json() or {}
    filename = (data.get("filename") or "").lower()
    mimetype = (data.get("mimetype") or "").lower()
    filesize = int(data.get("filesize") or 0)
    score = 0; signals=[]
    suspicious_ext = [".exe",".scr",".js",".vbs",".bat",".ps1",".jar"]
    for ext in suspicious_ext:
        if filename.endswith(ext):
            score += 40; signals.append(f"suspicious_ext:{ext}")
    if filesize > 50*1024*1024:
        score += 10; signals.append("large_file")
    if "invoice" in filename or "payment" in filename:
        score += 10; signals.append("phishy_filename")
    score = min(100, score)
    advice = "DON'T OPEN" if score>=50 else "Caution"
    try:
        db = get_db()
        db.execute("INSERT INTO attachments (filename,timestamp,score,signals) VALUES (?, ?, ?, ?)",
                   (filename, int(time.time()), score, ",".join(signals)))
        db.commit()
    except Exception as e:
        app.logger.error("DB insert attach failed: %s", e)
    return jsonify({"filename":filename,"mimetype":mimetype,"filesize":filesize,"score":score,"signals":signals,"advice":advice})

@app.route("/logs", methods=["GET"])
def logs():
    db = get_db()
    cur = db.execute("SELECT id,url,timestamp,heuristic_score,ml_prob,final_score,signals FROM scans ORDER BY id DESC LIMIT 50")
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
