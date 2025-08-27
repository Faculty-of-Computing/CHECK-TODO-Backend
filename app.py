from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import models

app = Flask(__name__)

# Enable CORS with support for cookies
CORS(app, supports_credentials=True)

# Use environment variable for secret key (fallback for local dev)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

@app.route("/")
def home():
    return {"message": "Todo Backend is running!"}


# Initialize DB
models.init_db()

# ----- AUTH -----
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if models.create_user(data["full_name"], data["email"], data["password"]):
        return jsonify({"message": "Account created successfully"}), 201
    return jsonify({"error": "Email already in use"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = models.get_user_by_email(data["email"])
    if user and models.check_password(user[3], data["password"]):
        session["user_id"] = user[0]
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"})


# ----- TASKS -----
@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    tasks = models.get_tasks(user_id)
    return jsonify(tasks)


@app.route("/tasks", methods=["POST"])
def add_task():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    models.add_task(user_id, data["title"])
    return jsonify({"message": "Task added"})


@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    models.update_task_status(task_id, data["completed"], user_id)
    return jsonify({"message": "Task updated"})


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    models.delete_task(task_id, user_id)
    return jsonify({"message": "Task deleted"})


if __name__ == "__main__":
    app.run(debug=True)
