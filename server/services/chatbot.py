import os
import torch
import json
import redis
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from groq import Groq
from datetime import datetime


# Load environment variables
load_dotenv()

# Get the connection URL from environment variables
POSTGRES_URL = os.getenv("POSTGRES_URL")
# Create the connection
pg_conn = psycopg2.connect(POSTGRES_URL, sslmode='require')
# Create the cursor
pg_cursor = pg_conn.cursor(cursor_factory=RealDictCursor)


# Set up models and connections
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
embedding_model = SentenceTransformer("thenlper/gte-base").to(device)
pc = Pinecone(api_key=os.getenv('pinecone_api'))
index = pc.Index("intellijobs")

# Set up Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD', ''),
    decode_responses=True  # Auto-decode bytes to strings
)

def get_embedding(text):
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []
    embedding = embedding_model.encode(text)
    return embedding.tolist()   

def get_similar_jobs(user_query, top_k=5):
    user_vector = get_embedding(user_query)
    results = index.query(vector=user_vector, top_k=top_k, include_metadata=True, include_values=False)
    return results
    
def read_markdown_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Update conversation in PostgreSQL
def update_conversation_in_postgres(conversation_id, user_id):
    try:
        # Get conversation data from Redis
        summary = redis_client.hget(f"conversation:{conversation_id}", "summary")
        messages = json.loads(redis_client.hget(f"conversation:{conversation_id}", "messages") or "[]")
        
        # Prepare conversation data
        conversation_data = {
            "conversation_id": conversation_id,
            "summary": summary,
            "history": messages
        }
        
        # Update PostgreSQL
        pg_cursor.execute("""
            UPDATE users 
            SET chatbot_conversations = chatbot_conversations || %s::jsonb
            WHERE user_id = %s
        """, (json.dumps(conversation_data), user_id))
        
        pg_conn.commit()
    except Exception as e:
        print(f"Error updating conversation in PostgreSQL: {e}")
        pg_conn.rollback()

# Create a new conversation or get existing one
def get_or_create_conversation(conversation_id=None):
    if conversation_id is None:
        # Create new conversation
        conversation_id = str(uuid.uuid4())
        # Initialize empty conversation history
        redis_client.hset(f"conversation:{conversation_id}", "summary", "")
        redis_client.hset(f"conversation:{conversation_id}", "messages", json.dumps([]))
        redis_client.hset(f"conversation:{conversation_id}", "created_at", json.dumps({}))
    else:
        # Try to get conversation from PostgreSQL first
        try:
            pg_cursor.execute("""
                SELECT chatbot_conversations 
                FROM users 
                WHERE chatbot_conversations::jsonb @> %s::jsonb
            """, (json.dumps({"conversation_id": conversation_id}),))
            
            result = pg_cursor.fetchone()
            if result:
                # Conversation found in PostgreSQL, store in Redis
                conversation_data = result[0]
                redis_client.hset(f"conversation:{conversation_id}", "summary", conversation_data.get("summary", ""))
                redis_client.hset(f"conversation:{conversation_id}", "messages", json.dumps(conversation_data.get("history", [])))
                redis_client.hset(f"conversation:{conversation_id}", "created_at", json.dumps({}))
            else:
                # If not in PostgreSQL, check Redis
                if not redis_client.exists(f"conversation:{conversation_id}"):
                    # If not in Redis either, create new
                    redis_client.hset(f"conversation:{conversation_id}", "summary", "")
                    redis_client.hset(f"conversation:{conversation_id}", "messages", json.dumps([]))
                    redis_client.hset(f"conversation:{conversation_id}", "created_at", json.dumps({}))
        except Exception as e:
            print(f"Error retrieving conversation from PostgreSQL: {e}")
            # Fallback to Redis if PostgreSQL fails
            if not redis_client.exists(f"conversation:{conversation_id}"):
                redis_client.hset(f"conversation:{conversation_id}", "summary", "")
                redis_client.hset(f"conversation:{conversation_id}", "messages", json.dumps([]))
                redis_client.hset(f"conversation:{conversation_id}", "created_at", json.dumps({}))
    
    # Return conversation data
    conversation_data = {
        "id": conversation_id,
        "summary": redis_client.hget(f"conversation:{conversation_id}", "summary"),
        "messages": json.loads(redis_client.hget(f"conversation:{conversation_id}", "messages") or "[]")
    }
    return conversation_data

# Add a message to conversation history
def add_message(conversation_id, role, content, user_id=None):
    # Get current messages
    messages_json = redis_client.hget(f"conversation:{conversation_id}", "messages")
    messages = json.loads(messages_json) if messages_json else []
    
    # Add new message
    messages.append({
        "role": role,
        "content": content
    })
    
    # Save updated messages
    redis_client.hset(f"conversation:{conversation_id}", "messages", json.dumps(messages))
    
    # If we have enough messages, update the summary
    if len(messages) % 4 == 0:  # Condense every 4 messages
        update_conversation_summary(conversation_id)
    
    # Update PostgreSQL if user_id is provided
    if user_id:
        try:
            # Get current time
            change_time = datetime.now().isoformat()
            
            # Prepare conversation data
            conversation_data = {
                "conversation_id": conversation_id,
                "history": messages,
                "change_time": change_time
            }
            
            # Update PostgreSQL
            pg_cursor.execute("""
                UPDATE users 
                SET chatbot_conversations = chatbot_conversations || %s::jsonb
                WHERE user_id = %s
            """, (json.dumps(conversation_data), user_id))
            
            pg_conn.commit()
        except Exception as e:
            print(f"Error updating conversation in PostgreSQL: {e}")
            pg_conn.rollback()
    
    return messages

# Use the LLM to create/update a condensed summary of the conversation
def update_conversation_summary(conversation_id):
    # Get current messages
    messages_json = redis_client.hget(f"conversation:{conversation_id}", "messages")
    if not messages_json:
        return
    
    messages = json.loads(messages_json)
    current_summary = redis_client.hget(f"conversation:{conversation_id}", "summary") or ""
    
    # Create a prompt for the LLM to condense the conversation
    formatted_messages = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-4:]])  # Last 4 messages
    
    summary_prompt = f"""
    Previous conversation summary: {current_summary}
    
    Recent conversation:
    {formatted_messages}
    
    Please create an updated summary of the entire conversation that includes only the important information.
    Focus on the user's job search preferences, specific requirements, and any important details mentioned.
    Keep it concise but comprehensive.
    """
    
    # Use Groq to generate the summary
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that creates concise, comprehensive summaries of job search conversations."
            },
            {
                "role": "user",
                "content": summary_prompt
            }
        ],
        temperature=0,
        max_tokens=500,
        top_p=1
    )
    
    new_summary = completion.choices[0].message.content
    
    # Save the updated summary
    redis_client.hset(f"conversation:{conversation_id}", "summary", new_summary)
    return new_summary

def generate_response(prompt, similar_jobs, conversation_id):
    # Get conversation summary
    conversation = get_or_create_conversation(conversation_id)
    conversation_summary = conversation["summary"]
    
    # Get job descriptions
    descriptions = '\n\n'.join([match['metadata']['description'] for match in similar_jobs['matches']])    
    
    # Read and populate template
    context_template = read_markdown_file('f:\Programming\IntelliJobs Project\intellijobs\server\context_template.md')
    
    # Add conversation history context to the template
    context = context_template.replace(
        '{{descriptions}}', descriptions
    ).replace(
        '{{prompt}}', prompt
    )
    
    # Add conversation history if available
    if conversation_summary:
        context += f"\n\nConversation History Summary:\n{conversation_summary}"
    
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {
                "role": "system",
                "content": "You are a conversational assistant who helps users with their job search. Your tasks include providing job listings relevant to the user's query and answering any questions related to these listings. Consider the user's conversation history when relevant."
            },
            {
                "role": "user",
                "content": context
            }
        ],
        temperature=0,
        max_tokens=2500,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    response_content = ""
    for chunk in completion:
        response_content += chunk.choices[0].delta.content or ""
    
    # Add the assistant's response to the conversation history
    add_message(conversation_id, "assistant", response_content)
    
    return response_content

def search_jobs(user_query, conversation_id=None, user_id=None):
    # Get or create conversation
    conversation = get_or_create_conversation(conversation_id)
    conversation_id = conversation["id"]
    
    # Add user message to history
    add_message(conversation_id, "user", user_query, user_id)
    
    # Get similar jobs
    similar_jobs = get_similar_jobs(user_query)
    
    # Generate response considering conversation history
    response = generate_response(user_query, similar_jobs, conversation_id)
    
    # Add assistant response to history
    add_message(conversation_id, "assistant", response, user_id)
    
    return {
        "response": response,
        "conversation_id": conversation_id
    }

# Example usage
if __name__ == "__main__":
    # First query (new conversation)
    result = search_jobs("I'm looking for software engineering jobs in San Francisco")
    print(f"Response: {result['response']}")
    print(f"Conversation ID: {result['conversation_id']}")
    
    # Second query (continue conversation)
    conversation_id = result['conversation_id']
    result2 = search_jobs("I prefer roles with Python and machine learning", conversation_id)
    print(f"Follow-up Response: {result2['response']}")
    
    # Print summary
    conversation = get_or_create_conversation(conversation_id)
    print(f"Conversation Summary: {conversation['summary']}")