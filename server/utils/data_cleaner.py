
import pandas as pd
import re
import json
import os

from pymongo import MongoClient
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()



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



documents = list(collection.find(query, {"_id": 0, "job_id": 1, "description": 1}))


df=pd.DataFrame(documents)



def clean_desc(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^\w\s\-\+.,]', '', text) # Remove non-alphanumeric characters except spaces, -, +, and .
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text) # Remove email addresses
    text = re.sub(r'http\S+', '', text) # Remove URLs    
    text = text.lower() # Convert to lowercase
    text = re.sub(r'\b(a|an|the)\b', '', text) # Remove articles (a, an, the)
    text = re.sub(r'\s+', ' ', text).strip()     # Remove unnecessary extra lines and spaces
    
    return text



df['description'] = df['description'].apply(clean_desc)



for _, row in df.iterrows():
    job_id = row['job_id']
    description = row['description']
    
    collection.update_one(
        {'job_id': job_id},  # Filter
        {'$set': {'description': description}}  # Update operation
    )

print("Update complete.")

