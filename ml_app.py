from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os
import base64
import json
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import io

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

# Load ML model and vectorizer from files
try:
    vectorizer = joblib.load('models/tfidf_vectorizer.joblib')
    clf = joblib.load('models/fake_news_model.joblib')
except Exception as e:
    print(f"Error loading models: {e}")
    print("Please ensure the model files exist in the 'models' directory")
    raise

async def extract_text_from_file(file: UploadFile):
    """Extract text from PDF or image file."""
    content = await file.read()
    
    if file.content_type == "application/pdf":
        # Handle PDF
        pdf = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    elif file.content_type.startswith("image/"):
        # Handle Image
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
        return text.strip()
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

@app.post("/api/predict")
async def predict_news(
    text: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        # Get content from either text or file
        if file:
            content = await extract_text_from_file(file)
        elif text:
            content = text
        else:
            raise HTTPException(status_code=400, detail="Please provide either text or file")

        if len(content.strip()) < 50:
            raise HTTPException(status_code=400, detail="Extracted text is too short")

        # ML Model prediction
        X = vectorizer.transform([content])
        prediction = clf.predict(X)[0]
        confidence = max(clf.predict_proba(X)[0])
        
        return {
            "prediction": "Real" if prediction == 1 else "Fake",
            "confidence": float(confidence),
            "extracted_text": content[:500] + "..." if len(content) > 500 else content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 