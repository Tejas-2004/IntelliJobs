from services.chatbot import search_jobs
from flask_cors import CORS
from flask import Flask, request, jsonify
from tasks import parse_resume_and_store
from dotenv import load_dotenv
import os
from psycopg2.extras import RealDictCursor
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
POSTGRES_URL = os.getenv("POSTGRES_URL")


@app.route('/')
def home():
    return 'Home route'


def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)


@app.route('/job-search', methods=['POST'])
def llm_response():
    data = request.json
    query = data.get('query')
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id')
    
    if not query:
        return jsonify({'error': 'Invalid input, missing query'}), 400

    response = search_jobs(query, conversation_id, user_id)
    return jsonify(response)

@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    data = request.json
    resume_data = data.get('resume_data')
    user_id = data.get('user_id')
    
    if not resume_data or not user_id:
        return jsonify({'error': 'Invalid input, missing resume_data or user_id'}), 400
    
    # Start background task
    task = parse_resume_and_store.delay(resume_data, user_id)
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = parse_resume_and_store.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', ''),
            'message': task.info.get('message', '')
        }
    else:
        response = {
            'state': task.state,
            'status': 'error',
            'message': str(task.info)
        }
    
    return jsonify(response)



@app.route("/api/sync-user", methods=["POST"])
def sync_user():
    data = request.get_json()
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        exists = cur.fetchone()

        if not exists:
            cur.execute(
                "INSERT INTO users (user_id) VALUES (%s);",
                (user_id,)
            )
            conn.commit()
            status = "inserted"
        else:
            status = "exists"

        cur.close()
        conn.close()
        return jsonify({"status": status}), 200

    except Exception as e:
        print("DB error:", e)
        return jsonify({"error": "Server error"}), 500






if __name__ == '__main__':
    app.run(debug=True)