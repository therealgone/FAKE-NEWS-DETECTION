# Fake News Detector - Technical Documentation

## System Architecture

The application uses a dual-verification approach combining machine learning and AI fact-checking:

### 1. Backend Components (app.py)

#### ML Model Verification
- Uses a trained scikit-learn model with TF-IDF vectorization
- Model trained on a dataset of real and fake news articles
- Provides classification (Real/Fake) with confidence score

#### Gemini AI Verification
- Utilizes Google's Gemini AI for fact-checking
- Analyzes article content, claims, and sources
- Provides detailed verification report

#### Input Processing
1. **URL Processing**
   - Extracts article content using BeautifulSoup
   - Captures metadata (title, author, date, source)
   - Handles various website structures

2. **File Processing**
   - PDF: Extracts text using PyPDF2
   - Images: Uses pytesseract for OCR
   - Handles multiple file formats

3. **Text Processing**
   - Cleans and normalizes input text
   - Removes special characters and formatting
   - Prepares text for model analysis

### 2. Frontend Components (frontend/)

#### User Interface (index.html, app.js)
- Modern, responsive dark theme design
- Multiple input methods (URL, file, text)
- Real-time validation and error handling
- Dynamic loading states
- Results display with confidence scores

#### Styling (styles.css)
- Custom dark theme implementation
- Responsive design for all screen sizes
- Animated loading states
- Error and success states

## Data Flow

1. **Input Reception**
   ```
   User Input → Frontend Validation → Backend API
   ```

2. **Processing Pipeline**
   ```
   Raw Input → Text Extraction → Text Preprocessing → Dual Analysis
   ```

3. **Analysis Flow**
   ```
   Preprocessed Text → ML Model Classification
                   → Gemini AI Analysis
                   → Results Compilation
   ```

4. **Response Delivery**
   ```
   Analysis Results → Frontend Rendering → User Display
   ```

## API Endpoints

### POST /verify-news
- **Purpose**: Main endpoint for news verification
- **Accepts**: FormData with one of:
  - `file`: PDF/Image file
  - `url`: News article URL
  - `text`: Article text
- **Returns**: JSON with:
  - ML model prediction and confidence
  - Gemini verification analysis
  - Article metadata (when available)
  - Error messages (if any)

## Error Handling

1. **Frontend Validation**
   - Input format validation
   - File size and type checks
   - URL format validation
   - Minimum text length requirements

2. **Backend Validation**
   - File processing errors
   - URL access errors
   - Text extraction failures
   - Model processing errors

## Performance Considerations

1. **Optimization Techniques**
   - Efficient text processing
   - Caching of model results
   - Asynchronous API calls
   - Optimized file handling

2. **Resource Management**
   - Memory-efficient file processing
   - Temporary file cleanup
   - Connection pooling
   - Error recovery mechanisms

## Security Measures

1. **Input Validation**
   - Sanitized file inputs
   - URL validation and sanitization
   - Text content validation

2. **API Security**
   - Rate limiting
   - Input size restrictions
   - Secure file handling
   - Environment variable protection

## Deployment Considerations

1. **Environment Setup**
   - Required environment variables
   - Dependencies installation
   - Model file placement
   - Temporary directory setup

2. **Server Configuration**
   - Port configuration
   - CORS settings
   - File upload limits
   - Error logging setup 