from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import httpx
from lxml import html

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

async def extract_text_from_url(url):
    """Extract text from URL using httpx and lxml."""
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = await client.get(url, headers=headers, timeout=15.0)
            response.raise_for_status()
            
            tree = html.fromstring(response.text)
            paragraphs = tree.xpath('//p/text()')
            article_text = ' '.join(p.strip() for p in paragraphs if p.strip())
            
            if not article_text:
                raise HTTPException(status_code=400, detail="Could not extract text from URL")
                
            return article_text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from URL: {str(e)}")

@app.post("/api/verify")
async def verify_news(
    url: str = Form(None),
    text: str = Form(None)
):
    try:
        content = text if text else await extract_text_from_url(url) if url else None
        if not content:
            raise HTTPException(status_code=400, detail="Please provide either URL or text content")

        prompt = f"""Analyze this news article for authenticity:
        {content[:3000]}
        
        Provide:
        1. Key claims verification
        2. Credibility assessment
        3. Final verdict
        """

        gemini_response = model.generate_content(prompt)
        
        return {
            "verification": gemini_response.text,
            "metadata": {
                "content_length": len(content),
                "source": url if url else "Direct text input"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 