import re
import string

def clean_text(text):
    """
    Clean and preprocess text for ML model
    - Convert to lowercase
    - Remove punctuation
    - Remove extra whitespace
    - Remove numbers
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text
