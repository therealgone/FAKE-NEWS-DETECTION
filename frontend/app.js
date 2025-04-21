function App() {
    const [file, setFile] = React.useState(null);
    const [url, setUrl] = React.useState('');
    const [text, setText] = React.useState('');
    const [result, setResult] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setUrl('');
        setText('');
        setError(null);
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
            const formData = new FormData();
            if (file) {
                formData.append('file', file);
            } else if (url) {
                formData.append('url', url);
            } else if (text) {
                formData.append('text', text);
            } else {
                throw new Error('Please provide a news article via file upload, URL, or text.');
            }

            const response = await fetch('http://localhost:8000/verify-news', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to verify news. Please try again.');
            }

            if (data.error) {
                throw new Error(data.error);
            }

            setResult(data);
        } catch (err) {
            console.error('Error:', err);
            setError(err.message || 'Failed to verify news. Please try again.');
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
        <div className="min-h-screen bg-[#1a1a1a] py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-100 mb-4">
                        Fake News Detector
                    </h1>
                    <p className="text-xl text-gray-300">
                        Verify news articles using AI and Gemini
                    </p>
                </div>

                <div className="bg-[#2d2d2d] rounded-lg border border-[rgba(255,255,255,0.1)] shadow-lg p-6">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Upload PDF or Image
                            </label>
                            <label className="custom-file-upload block">
                                <input
                                    type="file"
                                    className="file-input"
                                    accept=".pdf,image/*"
                                    onChange={handleFileChange}
                                />
                                {file ? file.name : 'Click to upload or drag and drop'}
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Or enter URL
                            </label>
                            <input
                                type="url"
                                value={url}
                                onChange={handleUrlChange}
                                className="input-field"
                                placeholder="https://example.com/news-article"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-200 mb-2">
                                Or paste text
                            </label>
                            <textarea
                                value={text}
                                onChange={handleTextChange}
                                className="input-field"
                                rows="4"
                                placeholder="Paste your news article text here..."
                            />
                        </div>

                        {inputError && (
                            <div className="text-red-400 text-sm">
                                {inputError}
                            </div>
                        )}

                        <button
                            type="submit"
                            className={`button w-full ${
                                loading || inputError
                                    ? 'opacity-50 cursor-not-allowed'
                                    : ''
                            }`}
                            disabled={loading || inputError}
                        >
                            {loading ? 'Verifying...' : 'Verify News'}
                        </button>
                    </form>
                </div>

                {loading && (
                    <div className="text-center">
                        <div className="loading mx-auto"></div>
                        <p className="mt-4 text-gray-300">Analyzing your news...</p>
                    </div>
                )}

                {error && (
                    <div className="bg-red-900/20 border border-red-500/50 text-red-400 px-4 py-3 rounded relative mb-8">
                        <strong className="font-bold">Error: </strong>
                        <span className="block sm:inline">{error}</span>
                        {error.includes('URL') && (
                            <p className="mt-2 text-sm">
                                Tip: Some news websites block automatic access. Try copying and pasting the article text directly.
                            </p>
                        )}
                    </div>
                )}

                {result && (
                    <div className="space-y-6">
                        <div className="result-card">
                            <h2 className="text-2xl font-bold mb-4 text-gray-100">Analysis Results</h2>
                            
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold mb-2 text-gray-200">Model Prediction</h3>
                                <p className={`text-xl ${result.model_prediction === 'Real' ? 'text-green-400' : 'text-red-400'}`}>
                                    {result.model_prediction} ({Math.round(result.confidence * 100)}% confidence)
                                </p>
                            </div>

                            <div className="mb-4">
                                <h3 className="text-lg font-semibold mb-2 text-gray-200">Gemini Verification</h3>
                                <div className="bg-[#242424] p-4 rounded-md">
                                    <pre className="whitespace-pre-wrap text-gray-300">{result.gemini_verification}</pre>
                                </div>
                            </div>

                            {result.metadata && Object.keys(result.metadata).length > 0 && (
                                <div className="mb-4">
                                    <h3 className="text-lg font-semibold mb-2 text-gray-200">Article Metadata</h3>
                                    <div className="bg-[#242424] p-4 rounded-md">
                                        <dl className="space-y-2">
                                            {Object.entries(result.metadata).map(([key, value]) => (
                                                <div key={key}>
                                                    <dt className="text-sm font-medium text-gray-400">{key}</dt>
                                                    <dd className="text-gray-300">{value}</dd>
                                                </div>
                                            ))}
                                        </dl>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root')); 