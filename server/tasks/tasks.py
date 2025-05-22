import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from services.resume_parser import resume_parser
import json
from datetime import datetime
from config.celery_config import celery_app
import PyPDF2
import docx
from flask_socketio import SocketIO

# Load environment variables
load_dotenv()

# Database connection
POSTGRES_URL = os.getenv("POSTGRES_URL")

def get_db_connection():
    return psycopg2.connect(POSTGRES_URL, cursor_factory=RealDictCursor)

@celery_app.task(name='tasks.tasks.scrape_and_update_vectors')
def scrape_and_update_vectors():
    try:
        from services.scraper import scrape_job_listings
        from services.embedder import update_pinecone
        
        # Scrape jobs
        scrape_job_listings()
        # Get embeddings and update Pinecone
        update_pinecone()
        return {"status": "success", "message": "Job scraping and vector update completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(name='tasks.tasks.parse_resume_and_store')
def parse_resume_and_store(resume_data, user_id):
    try:
        # Parse resume using resume_parser
        parsed_data = resume_parser(resume_data)
        parsed_json = json.loads(parsed_data)
        
        # Create embedding for the resume using the same model as for jobs
        from sentence_transformers import SentenceTransformer
        
        # Initialize the embedding model - use the same one as for job listings
        embedder = SentenceTransformer('thenlper/gte-base')
        
        # Combine relevant resume sections for embedding
        # Focus on the most important sections for job matching
        resume_text = f"{parsed_json.get('full name', '')} "
        resume_text += f"{parsed_json.get('technical skills', '')} "
        resume_text += f"{parsed_json.get('work experience', '')} "
        resume_text += f"{parsed_json.get('education details', '')} "
        resume_text += f"{parsed_json.get('projects', '')}"
        
        # Generate the embedding vector
        resume_vector = embedder.encode(resume_text)
        
        
        # Store in PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()
        change_time = datetime.now().isoformat()
        
        resume_info = {
            "parsed_data": parsed_json,
            "change_time": change_time,
            "vector": resume_vector.tolist()  # Store vector for future use
        }
        
        cur.execute("""
        UPDATE users
        SET resume_info = %s::jsonb
        WHERE user_id = %s
        """, (json.dumps(resume_info), user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Emit event to notify frontend
        socketio = SocketIO(message_queue='redis://localhost:6379/0')
        socketio.emit('resume_processed', {
            'userId': user_id, 
            'success': True,
        }, namespace='/resume')
        
        return {"status": "success", "message": "Resume parsed and stored successfully"}
        
    except Exception as e:
        # Emit failure event
        socketio = SocketIO(message_queue='redis://localhost:6379/0')
        socketio.emit('resume_processed', {'userId': user_id, 'success': False, 'error': str(e)}, namespace='/resume')
        
        return {"status": "error", "message": str(e)}
    



# @celery_app.task(name='tasks.tasks.parse_resume_and_store')
# def parse_resume_and_store(resume_data, user_id):
#     try:
#         # Parse resume using resume_parser
#         parsed_data = resume_parser(resume_data)
        
#         # Store in PostgreSQL
#         conn = get_db_connection()
#         cur = conn.cursor()
        
#         change_time = datetime.now().isoformat()
#         resume_info = {
#             "parsed_data": json.loads(parsed_data),
#             "change_time": change_time
#         }

#         cur.execute("""
#             UPDATE users
#             SET resume_info = %s::jsonb
#             WHERE user_id = %s
#         """, (json.dumps(resume_info), user_id))
#         conn.commit()
#         cur.close()
#         conn.close()
        
#         # Emit event to notify frontend
#         socketio = SocketIO(message_queue='redis://localhost:6379/0')
#         socketio.emit('resume_processed', {'userId': user_id, 'success': True}, namespace='/resume')
        
#         return {"status": "success", "message": "Resume parsed and stored successfully"}
#     except Exception as e:
#         # Emit failure event
#         socketio = SocketIO(message_queue='redis://localhost:6379/0')
#         socketio.emit('resume_processed', {'userId': user_id, 'success': False, 'error': str(e)}, namespace='/resume')
#         return {"status": "error", "message": str(e)}

@celery_app.task(name='tasks.tasks.process_resume')
def process_resume(file_path, user_id):
    try:
        # Read the file and extract text
        resume_text = ""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    resume_text += pdf_reader.pages[page_num].extract_text()
        elif file_extension in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                resume_text += para.text + "\n"
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # First update the resume path in the database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_exists = cur.fetchone() is not None
        
        if user_exists:
            cur.execute("UPDATE users SET resume_info = %s WHERE user_id = %s", 
                       (file_path, user_id))
        else:
            cur.execute("INSERT INTO users (user_id, resume_info) VALUES (%s, %s)", 
                       (user_id, file_path))
        
        conn.commit()
        cur.close()
        conn.close()
        
        # Now parse the resume text using the existing task
        parse_resume_and_store.delay(resume_text, user_id)
        
        return {"success": True, "message": "Resume file processed successfully"}
    except Exception as e:
        print(f"Error processing resume: {e}")
        # Send error notification
        socketio = SocketIO(message_queue='redis://localhost:6379/0')
        socketio.emit('resume_processed', {'userId': user_id, 'success': False, 'error': str(e)}, namespace='/resume')
        return {"success": False, "error": str(e)}
