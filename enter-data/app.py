
import os
from flask import Flask, jsonify, request
from models import db, Grade

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Student Grade Analytics - Enter Data"
    })


@app.route("/grades", methods=["POST"])
def enter_grade():
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
