import eventlet
eventlet.monkey_patch()


from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from psycopg2.extras import RealDictCursor
import psycopg2
from werkzeug.utils import secure_filename
from services.chatbot import search_jobs
from dotenv import load_dotenv
from tasks.tasks import process_resume, parse_resume_and_store

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://localhost:5000"]}})

# Celery configuration
app.config.update(
    CELERY=dict(
        broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        task_ignore_result=False
    )
)


# SocketIO setup with Redis message queue
socketio = SocketIO(app, cors_allowed_origins="*", message_queue='redis://localhost:6379/0')

# Upload folder setup
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Import celery config after app is created
from config.celery_config import celery_init_app
celery = celery_init_app(app)

POSTGRES_URL = os.getenv("POSTGRES_URL")

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)

@app.route('/')
def home():
    return 'Home route'

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

@app.route('/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    # Import task here to avoid circular imports
    from tasks.tasks import parse_resume_and_store
    
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

@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['resume']
    user_id = request.form.get('userId')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
        
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    try:
        # Save file to storage
        filename = f"{user_id}_{secure_filename(file.filename)}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Import task here to avoid circular imports
        from tasks.tasks import process_resume
        
        # Process resume asynchronously
        process_resume.delay(file_path, user_id)
        
        return jsonify({"success": True, "message": "Resume upload started"}), 200
        
    except Exception as e:
        print(f"Error uploading resume: {e}")
        return jsonify({"error": "Failed to upload resume", "details": str(e)}), 500

@app.route("/api/check-resume", methods=["POST"])
def check_resume():
    data = request.get_json()
    user_id = data.get("userId")
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query to check if user has a resume
        cur.execute("SELECT  resume_info FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        # Check if user exists and has a resume
        has_resume = user_data is not None and (user_data['resume_info'] != "None") and not (user_data['resume_info'].startswith("uploads"))
        
        return jsonify({"hasResume": has_resume})
    
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

# WebSocket connection handler
@socketio.on('connect', namespace='/resume')
def handle_connect():
    print('Client connected to WebSocket')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
