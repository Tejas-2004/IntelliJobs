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

        cur.execute("SELECT resume_info FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()

        if not user_data or not user_data['resume_info']:
            return jsonify({"hasResume": False})
        
        resume_info = user_data['resume_info']
        
        if resume_info == "None" or resume_info.startswith("uploads"):
            return jsonify({"hasResume": False})
        
        try:
            import json
            parsed_info = json.loads(resume_info)
            has_vector = 'vector' in parsed_info and len(parsed_info['vector']) > 0
            return jsonify({"hasResume": has_vector})
        except (json.JSONDecodeError, TypeError):
            return jsonify({"hasResume": False})

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route("/api/recommended-jobs", methods=["GET"])
def get_recommended_jobs():
    try:
        user_id = request.args.get('userId')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 6))
        skills = request.args.get('skills', '').split(',') if request.args.get('skills') else []
        remote = request.args.get('remote') == 'true'
        min_salary = request.args.get('minSalary')
        max_salary = request.args.get('maxSalary')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Get user's resume vector from PostgreSQL TEXT column containing JSON
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT resume_info
            FROM users 
            WHERE user_id = %s AND resume_info IS NOT NULL
        """, (user_id,))
        
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        
        if not user_data or not user_data['resume_info']:
            return jsonify({
                "jobs": [],
                "hasMore": False,
                "message": "No resume found for user"
            }), 200
        
        # Parse the JSON from TEXT column
        import json
        try:
            if user_data['resume_info'].startswith('uploads') or user_data['resume_info'] == 'None':
                return jsonify({
                    "jobs": [],
                    "hasMore": False,
                    "message": "Resume not processed yet"
                }), 200
            
            resume_info = json.loads(user_data['resume_info'])
            resume_vector = resume_info.get('vector')
            
            if not resume_vector or len(resume_vector) == 0:
                return jsonify({
                    "jobs": [],
                    "hasMore": False,
                    "message": "No vector found in resume data"
                }), 200
            
            resume_vector = [float(x) for x in resume_vector]
            
        except (json.JSONDecodeError, TypeError, ValueError, KeyError) as e:
            return jsonify({
                "jobs": [],
                "hasMore": False,
                "message": "Invalid resume data format"
            }), 200
        
        # Query Pinecone for similar jobs
        from pinecone import Pinecone
        import os
        
        pc = Pinecone(api_key=os.getenv('pinecone_api'))
        index = pc.Index('intellijobs')
        
        # Build metadata filter for Pinecone
        filter_conditions = {}
        
        if skills and skills != [''] and skills[0] != '':
            filter_conditions['keywords'] = {'$in': skills}
        
        if remote:
            filter_conditions['locations'] = {'$in': ['Remote', 'remote', 'REMOTE']}
        
        # Calculate offset for pagination
        offset = (page - 1) * limit
        total_to_fetch = offset + limit + 20
        
        # Query Pinecone
        query_response = index.query(
            vector=resume_vector,
            top_k=min(total_to_fetch, 100),
            include_metadata=True,
            filter=filter_conditions if filter_conditions else None
        )
        
        # Extract Pinecone IDs and similarity scores
        pinecone_matches = query_response.matches[offset:offset + limit]
        pinecone_ids = [match.id for match in pinecone_matches]
        similarity_scores = {match.id: match.score for match in pinecone_matches}
        
        if not pinecone_ids:
            return jsonify({
                "jobs": [],
                "hasMore": False,
                "message": "No matching jobs found"
            }), 200
        
        # Convert string IDs to integers for MongoDB query
        converted_ids = []
        for pid in pinecone_ids:
            try:
                converted_id = int(pid)
                converted_ids.append(converted_id)
            except (ValueError, TypeError):
                continue
        
        if not converted_ids:
            return jsonify({
                "jobs": [],
                "hasMore": False,
                "message": "No valid job IDs found"
            }), 200
        
        # Connect to MongoDB and fetch job details
        from pymongo import MongoClient
        
        mongo_client = MongoClient(os.getenv('mongo_uri'))
        db = mongo_client[os.getenv('MONGODB_DATABASE', 'job_listings')]
        jobs_collection = db['naukri_jobs']
        
        # Query MongoDB for jobs with matching job_id (using converted integers)
        mongo_jobs = list(jobs_collection.find({
            'job_id': {'$in': converted_ids}
        }))
        
        # Format jobs for frontend using actual MongoDB fields
        jobs = []
        for mongo_job in mongo_jobs:
            job_id = str(mongo_job.get('job_id'))
            
            # Find original string ID for similarity score lookup
            original_string_id = None
            for original_id in pinecone_ids:
                if int(original_id) == mongo_job.get('job_id'):
                    original_string_id = original_id
                    break
            
            similarity_score = similarity_scores.get(original_string_id, 0)
            match_percentage = round(similarity_score * 100)
            
            # Apply salary filter if specified
            if min_salary and max_salary:
                job_salary = mongo_job.get('salary', '')
                if job_salary and isinstance(job_salary, str):
                    import re
                    salary_numbers = re.findall(r'\d+', job_salary.replace(',', '').replace('$', '').replace('k', '000').replace('K', '000'))
                    if salary_numbers:
                        try:
                            avg_salary = sum(int(x) for x in salary_numbers) / len(salary_numbers)
                            min_sal_threshold = int(min_salary) * 1000
                            max_sal_threshold = int(max_salary) * 1000
                            if avg_salary < min_sal_threshold or avg_salary > max_sal_threshold:
                                continue
                        except ValueError:
                            pass
            
            # Format locations array as string
            locations = mongo_job.get('locations', [])
            location_str = ', '.join(locations) if isinstance(locations, list) else str(locations)
            
            # Get keywords array
            keywords = mongo_job.get('keywords', [])
            if not isinstance(keywords, list):
                keywords = []
            
            job = {
                'id': job_id,
                'pinecone_id': job_id,
                'title': mongo_job.get('title', ''),
                'company': mongo_job.get('company_name', ''),
                'logo': mongo_job.get('company_logo', '/placeholder.svg?height=40&width=40'),
                'location': location_str,
                'salary': mongo_job.get('salary', 'Not specified'),
                'tags': keywords,
                'posted': 'Recently posted',
                'description': mongo_job.get('description', ''),
                'match_percentage': match_percentage,
                'similarity_score': similarity_score,
                'experience': mongo_job.get('experience', ''),
                'job_url': mongo_job.get('job_url', ''),
                'rating': mongo_job.get('rating', 0),
                'review_count': mongo_job.get('review_count', 0),
                'locations_array': locations,
                'keywords_array': keywords,
                'requirements': [],
                'benefits': [],
                'responsibilities': [],
                'companyInfo': f"Rating: {mongo_job.get('rating', 'N/A')} ({mongo_job.get('review_count', 0)} reviews)" if mongo_job.get('rating') else f"{mongo_job.get('company_name', '')} - View company details"
            }
            jobs.append(job)
        
        # Sort jobs by similarity score (highest first)
        jobs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Determine if there are more results
        has_more = len(query_response.matches) > offset + limit
        
        mongo_client.close()
        
        return jsonify({
            "jobs": jobs,
            "hasMore": has_more,
            "total": len(query_response.matches),
            "page": page
        })
        
    except Exception as e:
        print(f"Error fetching recommended jobs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch recommended jobs", "details": str(e)}), 500
    


@app.route("/api/job-action", methods=["POST"])
def job_action():
    data = request.get_json()
    user_id = data.get("userId")
    job_id = str(data.get("jobId"))
    action = data.get("action")  # 'save', 'unsave', 'apply', 'unapply'
    action_type = data.get("type")  # 'saved' or 'applied'
    if not all([user_id, job_id, action, action_type]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT jobstats FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        import json
        if user_data and user_data['jobstats'] and user_data['jobstats'] != 'None':
            jobstats = json.loads(user_data['jobstats'])
        else:
            jobstats = {"saved": [], "applied": []}
        for key in ["saved", "applied"]:
            if key not in jobstats:
                jobstats[key] = []
        # Only touch the requested list!
        if action == "save" and job_id not in jobstats["saved"]:
            jobstats["saved"].append(job_id)
        elif action == "unsave" and job_id in jobstats["saved"]:
            jobstats["saved"].remove(job_id)
        elif action == "apply" and job_id not in jobstats["applied"]:
            jobstats["applied"].append(job_id)
        elif action == "unapply" and job_id in jobstats["applied"]:
            jobstats["applied"].remove(job_id)
        cur.execute("UPDATE users SET jobstats = %s WHERE user_id = %s", (json.dumps(jobstats), user_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "success": True,
            "jobstats": jobstats,
            "counts": {
                "saved": len(jobstats["saved"]),
                "applied": len(jobstats["applied"])
            }
        })
    except Exception as e:
        print(f"Error in job_action: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route("/api/user-job-actions", methods=["GET"])
def get_user_job_actions():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT jobstats FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        import json
        if not user_data or not user_data['jobstats'] or user_data['jobstats'] == 'None':
            return jsonify({"saved": [], "applied": []})
        jobstats = json.loads(user_data['jobstats'])
        return jsonify({
            "saved": jobstats.get("saved", []),
            "applied": jobstats.get("applied", [])
        })
    except Exception as e:
        print(f"Error getting user job actions: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500

@app.route("/api/job-stats", methods=["GET"])
def get_job_stats():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT jobstats FROM users WHERE user_id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        import json
        if not user_data or not user_data['jobstats'] or user_data['jobstats'] == 'None':
            return jsonify({"saved": 0, "applied": 0})
        jobstats = json.loads(user_data['jobstats'])
        return jsonify({
            "saved": len(jobstats.get("saved", [])),
            "applied": len(jobstats.get("applied", []))
        })
    except Exception as e:
        print(f"Error getting job stats: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500















# WebSocket connection handler
@socketio.on('connect', namespace='/resume')
def handle_connect():
    print('Client connected to WebSocket')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
