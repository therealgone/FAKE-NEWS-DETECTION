# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import cudf
import joblib
from cuml.feature_extraction.text import TfidfVectorizer

def load_test_samples():
    """Load 5 samples each from fake and real news."""
    # Load the datasets - adjust these paths to match your Google Drive structure
    fake = cudf.read_csv('/content/drive/MyDrive/archive/Fake.csv')
    real = cudf.read_csv('/content/drive/MyDrive/archive/True.csv')
    
    # Take 5 samples from each
    fake_samples = fake.sample(n=5, random_state=42)
    real_samples = real.sample(n=5, random_state=42)
    
    # Add labels
    fake_samples['label'] = 0
    real_samples['label'] = 1
    
    # Combine samples
    test_samples = cudf.concat([fake_samples, real_samples], ignore_index=True)
    
    return test_samples

def test_model():
    print("Loading test samples...")
    test_samples = load_test_samples()
    
    # Load the trained model and vectorizer
    print("Loading trained model and vectorizer...")
    vectorizer = joblib.load("/content/drive/MyDrive/Model/tfidf_vectorizer.joblib")
    model = joblib.load("/content/drive/MyDrive/Model/fake_news_model.joblib")
    
    # Prepare test data
    X_test = test_samples['text']
    y_test = test_samples['label']
    
    # Transform text using the trained vectorizer
    X_test_vec = vectorizer.transform(X_test)
    
    # Make predictions
    print("\nMaking predictions...")
    y_pred = model.predict(X_test_vec)
    
    # Calculate accuracy
    accuracy = (y_pred == y_test.values).mean()
    print(f"\nTest Accuracy: {accuracy:.4f}")
    
    # Display results for each article
    print("\nDetailed Results:")
    print("-" * 80)
    for i, (text, true_label, pred_label) in enumerate(zip(test_samples['text'].values, y_test.values, y_pred)):
        print(f"\nArticle {i+1}:")
        print(f"Text: {text[:200]}...")  # Show first 200 characters
        print(f"True Label: {'Real' if true_label == 1 else 'Fake'}")
        print(f"Predicted Label: {'Real' if pred_label == 1 else 'Fake'}")
        print(f"Correct: {'✓' if true_label == pred_label else '✗'}")
        print("-" * 80)

if __name__ == "__main__":
    test_model() 