import os
import json
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from backend.parser import extract_text

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), jd: str = Form(...)):
    # Step 1. Extract raw data from document
    file_bytes = await file.read()
    raw_resume_text = extract_text(file_bytes, file.filename)

    if not raw_resume_text:
        raise HTTPException(status_code=400, detail="Invalid file format or empty document.")
    
    # Step 2. GPT-4o Intelligence Pipeline
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an AI Resume Expert. Return only valid JSON. Analyze the resume against the JD."
                },
                {
                    "role": "user", 
                    "content": f"""
                    RESUME TEXT: {raw_resume_text}
                    JOB DESCRIPTION: {jd}
                    
                    Return a JSON object with:
                    1. 'ats_score': Int (0-100)
                    2. 'missing_keywords': List of strings
                    3. 'rewrites': List of objects with 'original' and 'optimized' 
                       (Use the 'Action-Result' framework for optimized bullets).
                    4. 'upskilling': List of 3 specific recommendations.
                    """
                }
            ],
            response_format={"type": "json_object"}
        )

        analysis_dict = json.loads(response.choices[0].message.content)
        
        return analysis_dict

    except Exception as e:
        # It's good practice to log the error to your terminal so you can see what happened
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)