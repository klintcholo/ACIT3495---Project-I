import os
import jwt
from flask import Flask, jsonify, request
from models import db, Grade

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
JWT_SECRET = os.environ["JWT_SECRET"]

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return jsonify({
        "message": "Student Grade Analytics - Enter Data"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "Healthy"
    }), 200


@app.route("/grades", methods=["POST"])
def enter_grade():

    # Step 1: Check authentication
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        return jsonify({"error": "Authentication required"}), 401

    token = authorization[7:]

    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid or expired token"}), 401

    # Step 2: Validate the grade data
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    student_id = data.get("student_id")
    course = data.get("course")
    grade = data.get("grade")

    if not isinstance(student_id, str) or not student_id.strip():
        return jsonify({"error": "Student ID is required"}), 400

    if not isinstance(course, str) or not course.strip():
        return jsonify({"error": "Course is required"}), 400

    if isinstance(grade, bool) or not isinstance(grade, (int, float)):
        return jsonify({"error": "Grade must be a number"}), 400

    if not 0 <= grade <= 100:
        return jsonify({"error": "Grade must be between 0 and 100"}), 400

    # Step 3: Save the grade to MySQL
    new_grade = Grade(
        student_id=student_id.strip(),
        course=course.strip(),
        grade=grade
    )

    db.session.add(new_grade)
    db.session.commit()

    return jsonify({
        "message": "Grade saved successfully",
        "student_id": new_grade.student_id,
        "course": new_grade.course,
        "grade": new_grade.grade
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)