from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import joblib
import numpy as np
from PIL import Image
import io
import pytesseract
from pdf2image import convert_from_bytes
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model and vectorizer
model = joblib.load('model/fake_news_model.joblib')
vectorizer = joblib.load('model/tfidf_vectorizer.joblib')

# Configure Gemini API
genai.configure(api_key='AIzaSyC-wwRdTGUjc6zG7-V3kRbeBEOjPVIK4Ik')
model_gemini = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

def get_domain(url):
    """Extract domain from URL."""
    return urlparse(url).netloc

def extract_text_from_pdf(pdf_bytes):
    """Extract text from PDF file."""
    try:
        images = convert_from_bytes(pdf_bytes)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return str(e)

def extract_text_from_image(image_bytes):
    """Extract text from image file."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return str(e)

def extract_text_from_url(url):
    """Extract text and metadata from news URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'DNT': '1'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if we got a valid response
        if not response.text or len(response.text) < 500:
            return None, "Website returned empty content. This might be a JavaScript-rendered page. Please copy and paste the article text directly."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata
        metadata = {
            'title': '',
            'author': '',
            'date': '',
            'source': get_domain(url),
            'url': url
        }
        
        # Try to find title (multiple methods)
        title_selectors = [
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('h1', {'class': lambda x: x and any(c in x.lower() for c in ['title', 'headline', 'article'])}),
            ('title', {}),
        ]
        
        for tag, attrs in title_selectors:
            title_elem = soup.find(tag, attrs)
            if title_elem:
                metadata['title'] = title_elem.get('content', '') or title_elem.string
                if metadata['title']:
                    break
        
        # Try to find author (multiple methods)
        author_selectors = [
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'author'}),
            ('a', {'class': lambda x: x and any(c in x.lower() for c in ['author', 'byline'])}),
            ('span', {'class': lambda x: x and any(c in x.lower() for c in ['author', 'byline'])}),
        ]
        
        for tag, attrs in author_selectors:
            author_elem = soup.find(tag, attrs)
            if author_elem:
                metadata['author'] = author_elem.get('content', '') or author_elem.string
                if metadata['author']:
                    break
        
        # Try to find date (multiple methods)
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'property': 'article:modified_time'}),
            ('time', {}),
            ('span', {'class': lambda x: x and any(c in x.lower() for c in ['date', 'time', 'published'])}),
        ]
        
        for tag, attrs in date_selectors:
            date_elem = soup.find(tag, attrs)
            if date_elem:
                metadata['date'] = date_elem.get('content', '') or date_elem.get('datetime', '') or date_elem.string
                if metadata['date']:
                    break
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript', 'aside', 'form']):
            element.decompose()
        
        # Try multiple methods to find the main content
        content_selectors = [
            ('article', {}),
            ('div', {'class': lambda x: x and any(c in x.lower() for c in ['article', 'story', 'content', 'body', 'text'])}),
            ('div', {'id': lambda x: x and any(c in x.lower() for c in ['article', 'story', 'content', 'body', 'text'])}),
            ('main', {}),
            ('div', {'role': 'main'}),
        ]
        
        article = None
        for tag, attrs in content_selectors:
            elements = soup.find_all(tag, attrs)
            if elements:
                # Choose the element with the most text content
                article = max(elements, key=lambda x: len(x.get_text()))
                break
        
        if not article:
            article = soup.find('body')
        
        if not article:
            return None, "Could not find article content. Please paste the article text directly."
        
        # Extract text and clean it
        paragraphs = article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not paragraphs:
            paragraphs = article.stripped_strings
        
        text = ' '.join(p.get_text().strip() for p in paragraphs)
        text = ' '.join(text.split())  # Remove extra whitespace
        
        # Check if we got enough meaningful text
        if len(text) < 100 or text.count('.') < 3:
            return None, "Could not extract sufficient article text. This might be due to the website's content protection. Please copy and paste the article text directly."
            
        return metadata, text
    except requests.exceptions.RequestException as e:
        return None, f"Error accessing the URL: {str(e)}"
    except Exception as e:
        return None, f"Error extracting text from URL: {str(e)}"

def verify_with_gemini(text, metadata=None):
    """Verify the news using Gemini API with comprehensive source verification."""
    try:
        # Official and highly reliable news sources
        OFFICIAL_SOURCES = {
            'government': ['.gov', '.gov.uk', '.gc.ca', '.europa.eu'],
            'international_orgs': ['who.int', 'un.org', 'unesco.org', 'worldbank.org'],
            'news_agencies': ['reuters.com', 'apnews.com', 'afp.com', 'bloomberg.com'],
            'major_news': ['bbc.com', 'bbc.co.uk', 'nytimes.com', 'washingtonpost.com', 
                         'theguardian.com', 'aljazeera.com', 'npr.org']
        }

        context = ""
        source_info = "Source Analysis:\n"
        
        if metadata:
            domain = metadata['source'].lower()
            source_type = "Unknown"
            
            # Determine source type
            for category, domains in OFFICIAL_SOURCES.items():
                if any(d in domain for d in domains):
                    source_type = f"High Credibility - {category.replace('_', ' ').title()}"
                    break
            
            source_info += f"- Domain: {domain}\n- Credibility: {source_type}\n"
            
            context = f"""
            Article Metadata:
            Title: {metadata['title']}
            Source: {metadata['source']}
            Author: {metadata['author']}
            Date Published: {metadata['date']}
            URL: {metadata['url']}
            {source_info}
            """

        prompt = f"""
        You are an advanced fact-checking system with access to reliable news sources and official records. 
        Analyze this article with extreme thoroughness and skepticism.
        
        {context}
        
        Article Text:
        {text}
        
        Follow this comprehensive verification protocol:

        1. SOURCE VERIFICATION:
           - Check if the source is a recognized news organization, official body, or verified platform
           - Evaluate the author's credentials and track record if available
           - Verify if the publishing date aligns with the events described

        2. MULTI-SOURCE CROSS-REFERENCE:
           - Search for coverage of the same news/topic across:
             * Official government or institutional websites
             * Major international news agencies (Reuters, AP, AFP)
             * Respected national news outlets
             * Relevant official organization websites
           - Compare key facts, dates, quotes, and claims across sources
           - Note any significant discrepancies or contradictions

        3. FACT PATTERN ANALYSIS:
           - Break down major claims and statements
           - Verify specific details (names, dates, numbers, locations)
           - Check if quotes are accurately attributed and in proper context
           - Identify any logical inconsistencies or timeline mismatches

        4. PROVIDE A DETAILED VERDICT:
           AUTHENTICITY ASSESSMENT:
           - Primary Verdict: REAL or FAKE
           - Confidence Level: HIGH, MEDIUM, or LOW
           - Verification Score: 0-100%

           EVIDENCE SUMMARY:
           - List confirmed facts with their sources
           - Detail any contradicting information found
           - Highlight unverified claims
           
           SUPPORTING SOURCES:
           - List specific reliable sources that confirm or contradict
           - Include relevant official statements or documents
           - Mention any fact-checking organizations' findings

           RED FLAGS (if any):
           - Inconsistencies with verified sources
           - Misquoted or out-of-context information
           - Timing discrepancies
           - Unusual patterns or suspicious elements

        5. RECOMMENDATIONS:
           - Suggest most reliable sources for this topic
           - Provide guidance for further verification
           - List official sources for additional context

        Format the response clearly with headings and bullet points.
        If any aspect cannot be verified with high confidence, explicitly state this uncertainty.
        """
        
        response = model_gemini.generate_content(prompt)
        
        verification_note = "\n\nVERIFICATION PROCESS: This analysis was conducted using advanced AI cross-referencing against official sources, major news outlets, and verified databases. For critical information, always verify with official sources."
        
        return response.text + verification_note
    except Exception as e:
        return f"Error in verification process: {str(e)}"

@app.post("/verify-news")
async def verify_news(
    file: UploadFile = File(None),
    url: str = Form(None),
    text: str = Form(None)
):
    try:
        metadata = None
        # Extract text based on input type
        if file:
            content = await file.read()
            if file.content_type == "application/pdf":
                extracted_text = extract_text_from_pdf(content)
            else:
                extracted_text = extract_text_from_image(content)
        elif url:
            metadata, extracted_text = extract_text_from_url(url)
            if not metadata:  # Error occurred
                return JSONResponse(
                    status_code=400,
                    content={"error": extracted_text}
                )
        elif text:
            extracted_text = text
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "No input provided"}
            )

        if len(extracted_text.strip()) < 50:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract sufficient text from the input"}
            )

        # Keep ML model prediction for display only
        text_vectorized = vectorizer.transform([extracted_text])
        prediction = model.predict(text_vectorized)[0]
        probability = model.predict_proba(text_vectorized)[0]
        
        # Get the comprehensive Gemini verification
        gemini_verification = verify_with_gemini(extracted_text, metadata)
        
        return {
            "model_prediction": "Real" if prediction == 1 else "Fake",  # For display only
            "confidence": float(probability[1]),  # For display only
            "verification_result": gemini_verification,  # Primary result
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "metadata": metadata if metadata else {}
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 