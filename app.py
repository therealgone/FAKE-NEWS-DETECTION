from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Load ML model and vectorizer
try:
    vectorizer = joblib.load('model/vectorizer.pkl')
    clf = joblib.load('model/model.pkl')
except:
    # For Vercel deployment, load models from environment variables
    import base64
    vectorizer = joblib.load(base64.b64decode(os.getenv("VECTORIZER_BASE64")))
    clf = joblib.load(base64.b64decode(os.getenv("MODEL_BASE64")))

def extract_text_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main content
        article_text = ""
        for p in soup.find_all('p'):
            article_text += p.get_text() + "\n"
            
        return article_text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from URL: {str(e)}")

@app.post("/api/verify-news")
async def verify_news(
    url: str = Form(None),
    text: str = Form(None)
):
    try:
        # Get text content
        content = text if text else extract_text_from_url(url) if url else None
        if not content:
            raise HTTPException(status_code=400, detail="Please provide either URL or text content")

        # ML Model prediction
        X = vectorizer.transform([content])
        prediction = clf.predict(X)[0]
        confidence = max(clf.predict_proba(X)[0])

        # Gemini verification
        prompt = f"""Analyze this news article for authenticity. Consider:
        1. Factual accuracy
        2. Source credibility
        3. Cross-reference with known facts
        4. Potential bias or misleading information

        Article text:
        {content[:5000]}  # Limit text length for Gemini

        Provide a structured analysis with:
        - Summary of key claims
        - Fact-checking results
        - Credibility assessment
        - Final verdict
        """

        gemini_response = model.generate_content(prompt)
        
        return {
            "model_prediction": "Real" if prediction == 1 else "Fake",
            "confidence": float(confidence),
            "gemini_verification": gemini_response.text,
            "metadata": {
                "content_length": len(content),
                "source": url if url else "Direct text input"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 