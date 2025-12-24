import os
import time
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_jwt_extended import JWTManager

from face_recognition_cnn import verify_face
from database import db, Violation
from user_model import User
from auth import create_token, role_required
from camera_service import get_frame
from face_service import analyze_face
from gaze_service import check_gaze
from liveness_service import detect_blink
from audio_service import detect_audio_cheating
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
# ⚙️ CONFIG (RENDER-SAFE SQLITE)
# ==================================================
DB_PATH = os.path.join("/tmp", "proctoring.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret")

# ==================================================
# 🔌 EXTENSIONS
# ==================================================
db.init_app(app)
jwt = JWTManager(app)

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
# 🔐 AUTH ROUTES
# ==================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            create_token(user.username, user.role)
            if user.role == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("exam"))

        return "Invalid credentials", 401

    return render_template("login.html")


# ==================================================
# 🎓 STUDENT ROUTES
# ==================================================

@app.route("/exam")
@role_required("student")
def exam():
    return render_template("exam.html")


@app.route("/monitor")
@role_required("student")
def monitor():
    frame = get_frame()
    if frame is None:
        return jsonify({"error": "Camera not working"})

    # FACE VERIFICATION
    verified, person = verify_face(frame)
    if not verified:
        events["MULTIPLE_FACES"] += 1

    # FACE + GAZE + BLINK
    face_status = analyze_face(frame)
    gaze_status = check_gaze(frame)
    blink = detect_blink(frame)

    if face_status != "SINGLE_FACE":
        events[face_status] += 1

    if gaze_status == "LOOKING_AWAY":
        events["LOOKING_AWAY"] += 1

    # AUDIO CHEATING
    audio_flag, speech_text = detect_audio_cheating()
    if audio_flag:
        events["AUDIO_DETECTED"] += 1

    # RISK CALCULATION
    risk = calculate_risk(events)

    # SAVE VIOLATION
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
# 👨‍💼 ADMIN ROUTES
# ==================================================

@app.route("/admin")
@role_required("admin")
def admin():
    logs = Violation.query.all()
    return render_template("admin.html", logs=logs)


# ==================================================
# ▶️ MAIN
# ==================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
