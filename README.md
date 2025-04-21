# Fake News Detection System
Jeevan Baabu Murugan
ADS Project

A modern web application that uses AI to detect and verify fake news articles. Built with FastAPI, React, and Google's Gemini AI.

## Features

- **Multiple Input Methods**:
  - Upload images (PNG, JPG, JPEG) or PDFs
  - Paste article URLs
  - Direct text input
  - Image preview with remove option
  - File size validation (10MB limit)

- **Advanced OCR**:
  - Cloud-based OCR using OCR.space API
  - Support for multiple languages
  - High accuracy text extraction
  - Automatic image enhancement

- **AI-Powered Analysis**:
  - Google Gemini AI integration
  - Cross-reference with multiple sources
  - Detailed verification reports
  - Confidence scoring

- **Modern UI/UX**:
  - Dark theme
  - Responsive design
  - Real-time feedback
  - Loading states
  - Error handling

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/fake-news-detection.git
   cd fake-news-detection
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   OCR_API_KEY=your_ocr_space_api_key
   ```

4. **Start the servers**:
   ```bash
   # Terminal 1 - Backend
   python app.py

   # Terminal 2 - Frontend
   python server.py
   ```

5. **Access the application**:
   Open http://localhost:3000 in your browser

## API Endpoints

- `POST /api/verify`: Main endpoint for news verification
  - Accepts: file upload, URL, or text
  - Returns: Verification results with confidence score

## Technologies Used

- **Backend**:
  - FastAPI
  - Google Gemini AI
  - OCR.space API
  - BeautifulSoup4
  - PyPDF2

- **Frontend**:
  - React
  - Tailwind CSS
  - Modern JavaScript

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for the verification engine
- OCR.space for OCR capabilities
- The open-source community for various tools and libraries 
