import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from typing import Optional
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
from PIL import Image
import datetime
import base64
from dotenv import load_dotenv
from xml.etree import ElementTree

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS middleware with more specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyAUXbOGCh23NtPYQfF0uPKit5XTtBuQRn4"
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# OCR.space API key
OCR_API_KEY = os.getenv("OCR_API_KEY", "K89675090788957")

def extract_text_from_url(url: str) -> str:
    """Extract text from a news article URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text from paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        if not text or len(text.strip()) < 50:
            raise ValueError("Could not extract sufficient text from the URL. Please try pasting the article text directly.")
            
        return text.strip()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error accessing URL: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing URL: {str(e)}")

def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text or len(text.strip()) < 50:
            raise ValueError(
                "Could not extract sufficient text from the PDF. "
                "Please ensure the PDF contains selectable text "
                "or try pasting the article text directly."
            )
        return text
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting text from PDF: {str(e)}"
        )

def extract_text_from_image(image_content: bytes) -> str:
    try:
        print("Starting image processing...")
        
        # Convert image to base64
        base64_image = base64.b64encode(image_content).decode()
        print("Image converted to base64")
        
        payload = {
            'apikey': OCR_API_KEY,
            'base64Image': f'data:image/jpeg;base64,{base64_image}',
            'language': 'eng',
            'detectOrientation': True,
            'scale': True,
            'OCREngine': 2
        }
        
        print("Making request to OCR.space API...")
        # Make request to OCR.space API
        response = requests.post(
            'https://api.ocr.space/parse/image',
            data=payload,
            timeout=30  # Increased timeout
        )
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text[:200]}...")  # Print first 200 chars of response
        
        if response.status_code != 200:
            raise ValueError(f"OCR API error: Status {response.status_code} - {response.text}")
            
        result = response.json()
        
        if result.get('OCRExitCode') != 1:
            raise ValueError(f"OCR processing failed: {result.get('ErrorMessage', 'Unknown error')}")
            
        # Extract text from response
        text = ' '.join([page.get('ParsedText', '') for page in result.get('ParsedResults', [])])
        
        if not text or len(text.strip()) < 50:
            raise ValueError(
                "Could not extract sufficient text from the image. "
                "Please ensure the image contains clear, readable text "
                "or try pasting the article text directly."
            )
        
        print(f"Successfully extracted {len(text)} characters of text")
        return text.strip()
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Network error while processing image: {str(e)}"
        )
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing OCR response: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}. "
                  "Please ensure the image is clear and contains readable text."
        )

def search_news_sources(query: str) -> list:
    try:
        # Extract key terms from the query for better search
        key_terms = ' '.join(query.split()[:10])  # Use first 10 words
        
        # Use Google News search
        search_url = f"https://news.google.com/rss/search?q={key_terms}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if response.status_code != 200:
            print(f"News search failed with status {response.status_code}")
            return []
            
        # Parse the RSS feed
        root = ElementTree.fromstring(response.content)
        
        # Extract news items
        news_items = []
        for item in root.findall('.//item')[:5]:  # Get top 5 news items
            title = item.find('title').text
            link = item.find('link').text
            news_items.append({
                'title': title,
                'link': link,
                'snippet': title  # Use title as snippet since we don't have description
            })
            
        return news_items
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []

def validate_file_size(file: UploadFile) -> None:
    # Check file size (10MB limit)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    file.file.seek(0, 2)  # Seek to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # Reset file pointer
    
    if file_size > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum limit of 10MB"
        )

@app.post("/api/verify")
async def verify_news(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    try:
        content = ""
        if file:
            print(f"Processing file: {file.filename}, Content-Type: {file.content_type}")
            # Validate file size
            validate_file_size(file)
            
            file_content = await file.read()
            content_type = file.content_type.lower()
            
            if content_type == 'application/pdf':
                content = extract_text_from_pdf(file_content)
            elif content_type.startswith('image/'):
                print("Processing image file...")
                content = extract_text_from_image(file_content)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type. Please upload a PDF or image file (PNG, JPG, JPEG)."
                )
        elif text:
            if text.startswith("URL: "):
                url = text[4:].strip()
                content = extract_text_from_url(url)
            else:
                content = text
        else:
            raise HTTPException(
                status_code=400,
                detail="Please provide either text or file"
            )

        if not content or len(content.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="The provided content is too short. Please provide a longer article text."
            )

        # Search for related news articles
        search_results = search_news_sources(content[:200])
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Prepare the prompt for Gemini
        prompt = f"""Analyze this news article and provide a clear, structured verification report. Current date: {current_date}

Article text:
{content}

Cross-reference with these sources:
{json.dumps(search_results, indent=2)}

Provide your analysis in this EXACT format:
1. VERDICT: [REAL/FAKE/UNVERIFIED] (Choose one only)
2. CONFIDENCE: [0-100%]
3. KEY CLAIMS:
   - Claim 1
   - Claim 2
   (List main claims briefly)

4. CROSS-REFERENCES:
   - Source 1: [URL] - [What they say]
   - Source 2: [URL] - [What they say]
   - Source 3: [URL] - [What they say]
   (At least 3 credible sources)

5. RED FLAGS (if any):
   - Flag 1
   - Flag 2
   (List any concerning elements)

6. TIMELINESS:
   - Article date: [Date]
   - Last verified: [Current date]
   - Is this current? [Yes/No]

Keep responses concise and factual. Focus on verifiable information."""

        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Return the verification result
        return {
            "verification": response.text
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error in verify_news: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify server status."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 