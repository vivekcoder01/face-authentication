import os
import time
from flask import Flask, render_template, jsonify, request, redirect, session

from database import db, Violation
from user_model import User

from camera_service import get_frame
from face_service import analyze_face
from gaze_service import check_gaze
from liveness_service import detect_blink
from audio_service import detect_audio_cheating
from face_recognition_cnn import verify_face
from risk_engine import calculate_risk

# ==================================================
# 🚀 APP INIT
# ==================================================
app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# ==================================================
# ⚙️ CONFIG (CLOUD + LOCAL SAFE)
# ==================================================
DB_PATH = os.path.join("/tmp", "proctoring.db")  # Render-safe
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "final-year-secret-key"

db.init_app(app)

with app.app_context():
    db.create_all()

# ==================================================
# 📊 EVENTS COUNTER
# ==================================================
events = {
    "NO_FACE": 0,
    "MULTIPLE_FACES": 0,
    "LOOKING_AWAY": 0,
    "AUDIO_DETECTED": 0
}

# ==================================================
# 🔐 LOGIN
# ==================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["username"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin")
            else:
                return redirect("/exam")

        return "Invalid credentials"

    return render_template("login.html")

# ==================================================
# 👨‍🎓 STUDENT EXAM
# ==================================================
@app.route("/exam")
def exam():
    if "role" not in session or session["role"] != "student":
        return redirect("/")

    return render_template("exam.html")

# ==================================================
# 🎥 MONITORING API
# ==================================================
@app.route("/monitor")
def monitor():
    if "role" not in session or session["role"] != "student":
        return jsonify({"error": "Unauthorized"}), 403

    frame = get_frame()
    if frame is None:
        return jsonify({"error": "Camera not working"})

    # Face verification (CNN)
    verified, person = verify_face(frame)
    if not verified:
        events["MULTIPLE_FACES"] += 1

    # Face & gaze
    face_status = analyze_face(frame)
    gaze_status = check_gaze(frame)
    blink = detect_blink(frame)

    if face_status != "SINGLE_FACE":
        events[face_status] += 1

    if gaze_status == "LOOKING_AWAY":
        events["LOOKING_AWAY"] += 1

    # Audio cheating
    audio_flag, speech_text = detect_audio_cheating()
    if audio_flag:
        events["AUDIO_DETECTED"] += 1

    # Risk calculation
    risk = calculate_risk(events)

    # Save violation
    violation = Violation(
        violation_type=face_status,
        risk_level=risk,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(violation)
    db.session.commit()

    return jsonify({
        "verified": verified,
        "person": person,
        "face": face_status,
        "gaze": gaze_status,
        "blink": blink,
        "audio_cheating": audio_flag,
        "speech": speech_text,
        "risk": risk,
        "events": events
    })

# ==================================================
# 👨‍💼 ADMIN PANEL
# ==================================================
@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    logs = Violation.query.all()
    return render_template("admin.html", logs=logs)

# ==================================================
# 🚪 LOGOUT
# ==================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ==================================================
# ▶️ RUN
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
