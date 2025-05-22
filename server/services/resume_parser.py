import os
from groq import Groq

def resume_parser(resume_data):
    prompt = '''
    You are an AI bot designed to act as a professional for parsing resumes. You are given with resume and your job is to extract the following information from the resume:
    1. full name
    2. email id
    3. phone number
    4. github portfolio
    5. linkedin id
    6. current location
    7. education details
    8. internships
    9. projects
    10. work experience
    11. certifications
    12. achievements
    13. languages known
    14. hobbies
    15. references
    16. technical skills
    17. soft skills
    Give the extracted information in json format only

    IMPORTANT: Your response must be ONLY valid JSON with no additional text, explanations, or markdown formatting. The JSON should start with { and end with } with no other characters before or after.
    '''
    
    # Create Groq client using environment variable
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": resume_data}
    ]
    
    # Get the complete response without streaming
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.0,
        max_tokens=1500
    )
    
    # Extract the complete response content
    response_content = completion.choices[0].message.content
    
    return response_content