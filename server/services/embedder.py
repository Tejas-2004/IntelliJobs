def get_embedding(text, model=None):
    """
    Convert text to vector embeddings using the SentenceTransformer model.
    
    Args:
        text (str): Text to be converted to embeddings
        model (SentenceTransformer, optional): Pre-loaded model to use for embeddings
        
    Returns:
        list: Vector embedding as a list of floats
    """
    if not text or not text.strip():
        print("Attempted to get embedding for empty text.")
        return []
    
    try:
        # If model is not provided, initialize it
        if model is None:
            import torch
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("thenlper/gte-base").to("cuda" if torch.cuda.is_available() else "cpu")
        
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []


def update_pinecone():
    """
    Fetch recent job listings from MongoDB, process them, generate embeddings,
    and update the Pinecone index with these vectors.
    
    Returns:
        dict: Status of the operation with details
    """
    try:
        import pandas as pd
        import os
        from pymongo import MongoClient
        from datetime import datetime
        from tqdm import tqdm
        from pinecone import Pinecone
        from dotenv import load_dotenv
        import torch
        from sentence_transformers import SentenceTransformer
        
        # Load environment variables
        load_dotenv()
        
        # Connect to MongoDB
        client = MongoClient(f"mongodb+srv://{os.getenv('mongo_user')}:{os.getenv('mongo_password')}@cluster0.y3ugmg6.mongodb.net/")
        db = client["job_listings"]
        collection = db["naukri_jobs"]
        
        # Define today's date string in 'YYYY-MM-DD' format
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Query to match documents where 'uploaded_at' contains today's date
        query = {
            "uploaded_at": {
                "$regex": f"^{today_str}"
            }
        }
        
        # Fetch data from MongoDB
        documents = list(collection.find(query, {"_id": 0}))
        
        if not documents:
            return {"status": "info", "message": "No new job listings found for today"}
        
        # Create DataFrame and select relevant columns
        df = pd.DataFrame(documents)
        columns_to_keep = ['job_id', 'title', 'description', 'locations', 'keywords', 
                          'company_name', 'experience', 'salary', 'rating', 'review_count']
        df = df[columns_to_keep]
        
        # Process location and keyword fields
        df['locations'] = df['locations'].apply(lambda x: ' '.join(map(str, x)))
        df['keywords'] = df['keywords'].apply(lambda x: ' '.join(map(str, x)))
        
        # Create combined description text
        df['combined_data'] = "The name of the company is "+df['company_name']+" The job role is "+df['title']+ \
                             " Technologies needed are or techstack is "+df['keywords']+" Locations are "+df['locations']+ \
                             " Experience needed is "+df['experience']+" Salary range is "+df['salary']+ \
                             " Rating is "+df['rating']+" and total ratings are "+str(df['review_count'])+ \
                             " Job description is "+df['description']
        
        # Initialize embedding model
        embedding_model = SentenceTransformer("thenlper/gte-base").to("cuda" if torch.cuda.is_available() else "cpu")
        
        # Generate embeddings with progress bar
        tqdm.pandas()
        df['embedding'] = df['combined_data'].progress_apply(lambda x: get_embedding(x, embedding_model))
        
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('pinecone_api'))
        index = pc.Index("intellijobs")
        
        # Prepare vectors for upsert
        vectors = [
            {
                'id': str(row['job_id']),
                'values': row['embedding'],
                'metadata': {'description': row['combined_data']}
            }
            for _, row in df.iterrows() if len(row['embedding']) > 0  # Skip empty embeddings
        ]
        
        # Upsert vectors in batches
        batch_size = 43
        for i in tqdm(range(0, len(vectors), batch_size), desc="Upserting vectors"):
            batch = vectors[i:i + batch_size]  # Extract batch
            index.upsert(batch)  # Upsert the batch of vectors
        
        return {
            "status": "success", 
            "message": f"Upsert complete: {len(vectors)} job listings processed",
            "total_jobs": len(df),
            "disclosed_salary_jobs": len(df) - df['salary'].str.lower().eq('not disclosed').sum()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}