# Accelerated Data Science Project
# Developed by Jeevan Baabu
# Fake News Detector


Fake News Detector

A full-stack application that uses AI and Google's Gemini model to detect and verify news articles. The application combines machine learning-based classification with advanced fact-checking capabilities.

## Features

- 🔍 Multiple input methods:
  - URL analysis
  - Direct text input
  - PDF/Image upload
- 🤖 Dual verification system:
  - ML model classification
  - Gemini AI fact-checking
- 🎨 Modern dark theme UI
- 📱 Responsive design
- ⚡ Real-time analysis

## Tech Stack

- **Backend**:
  - FastAPI
  - scikit-learn
  - Google Gemini AI
  - PyPDF2
  - pytesseract

- **Frontend**:
  - React
  - TailwindCSS
  - JavaScript

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fake-news-detector.git
cd fake-news-detector
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory and add:
```env
GEMINI_API_KEY=your_gemini_api_key
```

4. Start the backend server:
```bash
python app.py
```

5. Start the frontend server:
```bash
python server.py
```

6. Access the application at `http://localhost:3001`

## Project Structure

```
fake-news-detector/
├── app.py                 # FastAPI backend server
├── server.py             # Frontend server
├── model/
│   ├── model.pkl        # Trained ML model
│   └── vectorizer.pkl   # TF-IDF vectorizer
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── requirements.txt
```

## Usage

1. Open the application in your browser
2. Choose one of three input methods:
   - Upload a PDF/Image file
   - Enter a news article URL
   - Paste the article text directly
3. Click "Verify News"
4. View the analysis results:
   - ML model prediction with confidence score
   - Gemini AI fact-checking analysis
   - Article metadata (when available)

## API Endpoints

- `POST /verify-news`
  - Accepts: FormData with either file, url, or text
  - Returns: JSON with analysis results

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
