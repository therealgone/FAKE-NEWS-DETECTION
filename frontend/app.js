const { useState } = React;
const { createRoot } = ReactDOM;

function App() {
    console.log('App component rendering'); // Debug log

    const [file, setFile] = useState(null);
    const [filePreview, setFilePreview] = useState(null);
    const [url, setUrl] = useState('');
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [serverStatus, setServerStatus] = useState('checking'); // 'checking', 'online', 'offline'

    // Check server status on component mount
    React.useEffect(() => {
        const checkServerStatus = async () => {
            try {
                console.log('Checking server status...');
                const response = await fetch('http://localhost:8000/api/health', {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    },
                    mode: 'cors',
                });
                
                console.log('Server status response:', response.status);
                if (response.ok) {
                    setServerStatus('online');
                    console.log('Server is online');
                } else {
                    setServerStatus('offline');
                    console.log('Server returned error status');
                }
            } catch (err) {
                console.error('Server connection error:', err);
                setServerStatus('offline');
            }
        };
        
        checkServerStatus();
        
        // Set up periodic server status check
        const intervalId = setInterval(checkServerStatus, 10000); // Check every 10 seconds
        
        // Clean up interval on component unmount
        return () => clearInterval(intervalId);
    }, []);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            // Create preview URL for image files
            if (selectedFile.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setFilePreview(reader.result);
                };
                reader.readAsDataURL(selectedFile);
            } else {
                setFilePreview(null);
            }
            setUrl('');
            setText('');
            setError(null);
        }
    };

    const handleRemoveFile = () => {
        setFile(null);
        setFilePreview(null);
    };

    const handleUrlChange = (e) => {
        setUrl(e.target.value);
        setFile(null);
        setText('');
        setError(null);
    };

    const handleTextChange = (e) => {
        setText(e.target.value);
        setFile(null);
        setUrl('');
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            if (!file && !url && !text) {
                throw new Error('Please provide a news article via file upload, URL, or text.');
            }

            // Check if server is online
            if (serverStatus === 'offline') {
                throw new Error('Server is currently offline. Please try again later.');
            }

            const formData = new FormData();
            
            // If file is provided
            if (file) {
                console.log('Uploading file:', file.name, file.type);
                formData.append('file', file);
            } 
            // If URL is provided
            else if (url) {
                console.log('Processing URL:', url);
                formData.append('text', `URL: ${url}`);
            } 
            // If text is provided
            else if (text) {
                console.log('Processing text input');
                formData.append('text', text);
            }

            console.log('Sending request to backend...');
            
            // Add timeout to fetch request
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
            
            const response = await fetch('http://localhost:8000/api/verify', {
                method: 'POST',
                body: formData,
                signal: controller.signal,
                mode: 'cors',
            });
            
            clearTimeout(timeoutId);

            console.log('Response status:', response.status);
            const responseText = await response.text();
            console.log('Response text:', responseText);

            if (!response.ok) {
                let errorMessage;
                try {
                    const errorData = JSON.parse(responseText);
                    errorMessage = errorData.detail || 'Failed to verify the article. Please try again.';
                } catch (e) {
                    errorMessage = responseText || 'Failed to verify the article. Please try again.';
                }
                throw new Error(errorMessage);
            }

            const data = JSON.parse(responseText);
            setResult(data);

            // Clear inputs after successful submission
            setFile(null);
            setFilePreview(null);
            setUrl('');
            setText('');

        } catch (err) {
            console.error('Error:', err);
            
            // Handle specific error types
            if (err.name === 'AbortError') {
                setError('Request timed out. The server is taking too long to respond. Please try again.');
            } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                setError('Could not connect to the server. Please check if the server is running and try again.');
                setServerStatus('offline');
            } else {
                setError(err.message);
            }
        } finally {
            setLoading(false);
        }
    };

    const getInputErrorMessage = () => {
        if (!file && !url && !text) {
            return 'Please provide a news article via file upload, URL, or text.';
        }
        if (url && !url.startsWith('http')) {
            return 'Please enter a valid URL starting with http:// or https://';
        }
        if (text && text.length < 50) {
            return 'Please enter more text (at least 50 characters)';
        }
        return null;
    };

    const inputError = getInputErrorMessage();

    return (
        <div className="main-container">
            <h1 className="page-title">Fake News Detector</h1>
            <p className="sub-title">Accelerated Data Science Project</p>
            <p className="author-credit">Developed by Jeevan Baabu</p>
            
            {/* Server Status Indicator */}
            {serverStatus === 'offline' && (
                <div className="server-status-error">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span>Server is offline. Please try again later.</span>
                </div>
            )}
            
            <form onSubmit={handleSubmit} className="input-container w-full max-w-3xl">
                {/* File Upload */}
                <div className="mb-6">
                    <label htmlFor="file" className="block text-sm font-medium text-gray-300 mb-2">
                        Upload News Article
                    </label>
                    {!file ? (
                        <div className="custom-file-upload">
                            <div className="space-y-1 text-center">
                                <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <div className="flex text-sm text-gray-400 justify-center">
                                    <label htmlFor="file" className="relative cursor-pointer font-medium text-indigo-400 hover:text-indigo-300">
                                        <span>Upload a file</span>
                                        <input id="file" name="file" type="file" onChange={handleFileChange} className="sr-only" accept=".pdf,image/*" />
                                    </label>
                                    <p className="pl-1">or drag and drop</p>
                                </div>
                                <p className="text-xs text-gray-400">
                                    PDF, PNG, JPG, JPEG up to 10MB
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="file-preview-container">
                            <div className="file-preview-content">
                                {filePreview ? (
                                    <img src={filePreview} alt="Preview" className="file-preview-image" />
                                ) : (
                                    <svg className="h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                                    </svg>
                                )}
                                <div className="file-preview-info">
                                    <p className="file-preview-name">{file.name}</p>
                                    <p className="file-preview-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={handleRemoveFile}
                                className="remove-file-button"
                            >
                                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    )}
                </div>

                <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-600"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-dark-200 text-gray-400">OR</span>
                    </div>
                </div>

                {/* URL Input */}
                <div className="mb-6">
                    <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
                        Enter News Article URL
                    </label>
                    <input
                        type="url"
                        id="url"
                        value={url}
                        onChange={handleUrlChange}
                        className="input-field"
                        placeholder="https://example.com/article"
                    />
                </div>

                <div className="relative my-8">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-gray-600"></div>
                    </div>
                    <div className="relative flex justify-center text-sm">
                        <span className="px-2 bg-dark-200 text-gray-400">OR</span>
                    </div>
                </div>

                {/* Text Input */}
                <div className="mb-6">
                    <label htmlFor="text" className="block text-sm font-medium text-gray-300 mb-2">
                        Paste Article Text
                    </label>
                    <textarea
                        id="text"
                        value={text}
                        onChange={handleTextChange}
                        rows="4"
                        className="input-field"
                        placeholder="Paste the article text here..."
                    ></textarea>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="error-message">
                        <div className="flex">
                            <div className="flex-shrink-0">
                                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <div className="ml-3">
                                <p className="text-sm text-red-400">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={loading || (!file && !url && !text) || serverStatus === 'offline'}
                    className="button"
                >
                    {loading ? (
                        <div className="flex items-center justify-center">
                            <div className="loading mr-3"></div>
                            <span>Analyzing...</span>
                        </div>
                    ) : (
                        'Verify Article'
                    )}
                </button>
            </form>

            {/* Results Section */}
            {result && (
                <div className="result-card w-full max-w-3xl mt-8">
                    <h2 className="text-xl font-semibold mb-4 text-gray-100">Verification Results</h2>
                    <div className="prose prose-invert max-w-none">
                        <div dangerouslySetInnerHTML={{ 
                            __html: result.verification.replace(/\n/g, '<br>')
                                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                .replace(/- ([^\n]+)/g, '• $1')
                        }} />
                    </div>
                </div>
            )}
        </div>
    );
}

// Create root and render
const root = createRoot(document.getElementById('root'));
root.render(<App />);

// Make App available globally
window.App = App; 