import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

def load_data(sample_size=0.1):
    """Load and preprocess the fake news dataset."""
    # Load true and fake news datasets
    true_df = pd.read_csv('True.csv')
    fake_df = pd.read_csv('Fake.csv')
    
    # Add labels
    true_df['label'] = 1  # 1 for true news
    fake_df['label'] = 0  # 0 for fake news
    
    # Combine datasets
    df = pd.concat([true_df, fake_df], ignore_index=True)
    
    # Sample the data if requested
    if sample_size < 1.0:
        df = df.sample(frac=sample_size, random_state=42)
    
    return df

def train_model(X_train, y_train, X_test, y_test):
    """Train the model and evaluate its performance."""
    # Create and train TF-IDF vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train logistic regression model
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train_tfidf, y_train)
    
    # Evaluate model
    train_score = clf.score(X_train_tfidf, y_train)
    test_score = clf.score(X_test_tfidf, y_test)
    
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Testing accuracy: {test_score:.4f}")
    
    return vectorizer, clf

def main():
    """Main function to train and save the model."""
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Load and preprocess data
    print("Loading data...")
    df = load_data(sample_size=0.1)
    
    # Split features and target
    X = df['text']
    y = df['label']
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("Training model...")
    vectorizer, clf = train_model(X_train, y_train, X_test, y_test)
    
    # Save model and vectorizer
    print("Saving model and vectorizer...")
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.joblib')
    joblib.dump(clf, 'models/fake_news_model.joblib')
    
    print("Training complete! Model and vectorizer saved in 'models' directory.")

if __name__ == "__main__":
    main() 