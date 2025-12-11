from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'comentarios.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_comments_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            comment TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def resumen():
    return "API de Comentarios Activa. Usa /api/comments para interactuar (GET/POST)."

@app.route("/api/comments", methods=["GET", "POST"])
def handle_comments():
    conn = get_db_connection()
    if request.method == "POST":
        data = request.get_json()
        author = data.get("author")
        comment = data.get("comment")
        if author and comment:
            conn.execute("INSERT INTO comments (author, comment) VALUES (?, ?)", (author, comment))
            conn.commit()
            conn.close()
            return jsonify({"status": "success", "author": author, "comment": comment}), 201
        conn.close()
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400
    
    comments = conn.execute("SELECT * FROM comments ORDER BY timestamp DESC").fetchall()
    conn.close()
    return jsonify([dict(row) for row in comments])

if __name__ == "__main__":
    create_comments_table()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)