import base64
import joblib

def convert_model_to_base64(model_path):
    """Convert a model file to base64 string."""
    with open(model_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def main():
    # Convert vectorizer
    vectorizer_base64 = convert_model_to_base64('model/vectorizer.pkl')
    with open('vectorizer_base64.txt', 'w') as f:
        f.write(vectorizer_base64)
    print("Vectorizer converted and saved to vectorizer_base64.txt")

    # Convert model
    model_base64 = convert_model_to_base64('model/model.pkl')
    with open('model_base64.txt', 'w') as f:
        f.write(model_base64)
    print("Model converted and saved to model_base64.txt")

if __name__ == "__main__":
    main() 