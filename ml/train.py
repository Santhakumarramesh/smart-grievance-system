import pandas as pd
import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.text_clean import clean_text

def train_classifier():
    """
    Train the grievance classification model
    """
    print("="*60)
    print("Training Grievance Classification Model")
    print("="*60)
    
    # Load dataset
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'indian_grievance_dataset.csv')
    
    if not os.path.exists(data_path):
        print(f"✗ Dataset not found at {data_path}")
        return
    
    df = pd.read_csv(data_path)
    print(f"✓ Loaded dataset with {len(df)} samples")
    print(f"✓ Departments: {df['department'].nunique()}")
    print(f"\nDepartment distribution:")
    print(df['department'].value_counts())
    
    # Clean text
    print("\n" + "="*60)
    print("Cleaning text...")
    df['cleaned_complaint'] = df['complaint'].apply(clean_text)
    print("✓ Text cleaning completed")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_complaint'], 
        df['department'], 
        test_size=0.2, 
        random_state=42,
        stratify=df['department']
    )
    
    print(f"✓ Train set: {len(X_train)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    
    # Create TF-IDF vectorizer
    print("\n" + "="*60)
    print("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    print(f"✓ Vocabulary size: {len(vectorizer.vocabulary_)}")
    
    # Train Logistic Regression
    print("\n" + "="*60)
    print("Training Logistic Regression model...")
    model = LogisticRegression(
        max_iter=2000,
        random_state=42,
        multi_class='multinomial',
        solver='lbfgs'
    )
    
    model.fit(X_train_vectorized, y_train)
    print("✓ Model training completed")
    
    # Evaluate
    print("\n" + "="*60)
    print("Evaluating model...")
    y_pred = model.predict(X_test_vectorized)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and vectorizer
    print("\n" + "="*60)
    print("Saving model and vectorizer...")
    
    artifacts_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    model_path = os.path.join(artifacts_dir, 'model.joblib')
    vectorizer_path = os.path.join(artifacts_dir, 'vectorizer.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"✓ Model saved to: {model_path}")
    print(f"✓ Vectorizer saved to: {vectorizer_path}")
    
    # Test predictions
    print("\n" + "="*60)
    print("Testing predictions on sample complaints:")
    print("="*60)
    
    test_complaints = [
        "Street lights not working in our area",
        "Water supply is very irregular",
        "Garbage not collected for many days",
        "Road has many potholes",
        "Hospital lacks medicines"
    ]
    
    for complaint in test_complaints:
        cleaned = clean_text(complaint)
        vectorized = vectorizer.transform([cleaned])
        prediction = model.predict(vectorized)[0]
        print(f"\nComplaint: {complaint}")
        print(f"Predicted Department: {prediction}")
    
    print("\n" + "="*60)
    print("✓ Training completed successfully!")
    print("="*60)

if __name__ == '__main__':
    train_classifier()
