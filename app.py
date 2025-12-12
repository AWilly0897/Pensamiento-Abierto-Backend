from flask import Flask, request, jsonify
import os
import psycopg2 # Importamos la librería de PostgreSQL

app = Flask(__name__)

# Render nos da la URL de la base de datos a través de esta variable de entorno
DATABASE_URL = os.environ.get('DATABASE_URL') 

def get_db_connection():
    # Conectamos usando la URL de Render
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def create_comments_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            author TEXT NOT NULL,
            comment TEXT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ... (El resto de tus rutas @app.route puede permanecer igual, pero las consultas SQL deben adaptarse ligeramente a Postgres/psycopg2) ...
@app.route("/api/comments", methods=["GET", "POST"])
def handle_comments():
    conn = get_db_connection()
    # Usamos cursor para ejecutar comandos con psycopg2
    cur = conn.cursor() 

    if request.method == "POST":
        data = request.get_json()
        author = data.get("author")
        comment = data.get("comment")
        if author and comment:
            # psycopg2 usa %s como marcador de posición, no ?
            cur.execute("INSERT INTO comments (author, comment) VALUES (%s, %s)", (author, comment))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "success", "author": author, "comment": comment}), 201
        cur.close()
        conn.close()
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400
    
    # Para GET: Usamos fetchall para obtener resultados como lista de tuplas
    cur.execute("SELECT author, comment, timestamp FROM comments ORDER BY timestamp DESC")
    comments_data = cur.fetchall()
    cur.close()
    conn.close()
    
    # Formatear la respuesta para que sea legible en JSON
    comments_list = []
    for row in comments_data:
        comments_list.append({
            "author": row[0],
            "comment": row[1],
            "timestamp": row[2].isoformat() # Convertir fecha a string ISO
        })

    return jsonify(comments_list)

if __name__ == "__main__":
    create_comments_table()
    port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port) # Esto ya no se usa con gunicorn
    # Lo ejecutará gunicorn en Render.
    pass # El script no necesita app.run() si usas gunicorn