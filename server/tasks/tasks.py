from server.config.celery_config import celery_app
from server.services.scraper import scrape_job_listings
from server.services.embedder import get_embedding, update_pinecone
from server.services.resume_parser import resume_parser
import psycopg2
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host=os.getenv('PGHOST'),
    database=os.getenv('PGDATABASE'),
    user=os.getenv('PGUSER'),
    password=os.getenv('PGPASSWORD')
)
pg_cursor = pg_conn.cursor()

@celery_app.task
def scrape_and_update_vectors():
    try:
        # Scrape jobs
        scrape_job_listings()
        
        # Get embeddings and update Pinecone
        data=update_pinecone()
        
        return {"status": "success", "message": "Job scraping and vector update completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def parse_resume_and_store(self, resume_data, user_id):
    try:
        # Parse resume using Groq
        parsed_data = resume_parser(resume_data)
        
        # Store in PostgreSQL
        change_time = datetime.now().isoformat()
        resume_info = {
            "parsed_data": json.loads(parsed_data),
            "change_time": change_time
        }
        
        pg_cursor.execute("""
            UPDATE users 
            SET resume_info = %s::jsonb
            WHERE user_id = %s
        """, (json.dumps(resume_info), user_id))
        
        pg_conn.commit()
        
        # Emit event to notify frontend
        from app import socketio
        socketio.emit('resume_completed', {'user_id': user_id}, room=user_id)
        
        return {"status": "success", "message": "Resume parsed and stored successfully"}
    except Exception as e:
        pg_conn.rollback()
        # Emit failure event
        from app import socketio
        socketio.emit('resume_failed', {'user_id': user_id}, room=user_id)
        return {"status": "error", "message": str(e)}