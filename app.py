from flask import Flask, request, jsonify
import sqlite3
from models import create_tables, get_connection

app = Flask(__name__)

# Initialize DB
create_tables()

# ========== AUTH ROUTES ==========
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Signup successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username or email already exists"}), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get("username") or data.get("email")
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE (username=? OR email=?) AND password=?",
                (username_or_email, username_or_email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "user_id": user[0]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# ========== TASK ROUTES ==========
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    user_id = data.get("user_id")
    title = data.get("title")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    category = data.get("category", "")

    if not user_id or not title:
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (user_id, title, description, priority, category) VALUES (?, ?, ?, ?, ?)",
                (user_id, title, description, priority, category))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task added successfully"}), 201


@app.route('/tasks', methods=['GET'])
def get_tasks():
    priority = request.args.get("priority")
    category = request.args.get("category")

    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if priority:
        query += " AND priority=?"
        params.append(priority)
    if category:
        query += " AND category=?"
        params.append(category)

    cur.execute(query, params)
    tasks = cur.fetchall()
    conn.close()

    tasks_list = [
        {
            "id": t[0],
            "user_id": t[1],
            "title": t[2],
            "description": t[3],
            "priority": t[4],
            "category": t[5]
        }
        for t in tasks
    ]

    return jsonify(tasks_list), 200


if __name__ == '__main__':
    app.run(debug=True)
