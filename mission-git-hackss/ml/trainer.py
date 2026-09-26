"""Machine learning model trainer for challenge classification"""

import pickle
import logging
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


class ChallengeClassifierTrainer:
    """Train ML model for challenge classification"""
    
    CATEGORIES = ['web', 'crypto', 'pwn', 'reversing', 'forensics', 'osint', 'misc']
    
    def __init__(self):
        self.logger = logging.getLogger('md-exploit-engine.ml')
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def prepare_data(self, challenges: List[dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data from challenges
        
        Args:
            challenges: List of dicts with 'text' and 'category' keys
        
        Returns:
            X, y arrays for training
        """
        texts = [c['text'] for c in challenges]
        categories = [c['category'] for c in challenges]
        
        X = self.vectorizer.fit_transform(texts)
        y = np.array(categories)
        
        return X, y
    
    def train(self, challenges: List[dict], test_size: float = 0.2):
        """
        Train the classifier
        
        Args:
            challenges: Training data
            test_size: Fraction of data to use for testing
        """
        self.logger.info(f"Training on {len(challenges)} challenges")
        
        X, y = self.prepare_data(challenges)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.logger.info("Training classifier...")
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        report = classification_report(y_test, y_pred)
        
        self.logger.info(f"Classification Report:\n{report}")
        
        accuracy = self.classifier.score(X_test, y_test)
        self.logger.info(f"Accuracy: {accuracy:.2%}")
    
    def save_model(self, path: str):
        """Save trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'classifier': self.classifier
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.classifier = model_data['classifier']
        
        self.logger.info(f"Model loaded from {path}")
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict category for text
        
        Returns:
            (category, confidence)
        """
        X = self.vectorizer.transform([text])
        category = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = max(probabilities)
        
        return category, confidence


def create_sample_training_data() -> List[dict]:
    """Create sample training data for demonstration"""
    return [
        {'text': 'web application sql injection xss', 'category': 'web'},
        {'text': 'http server website vulnerability', 'category': 'web'},
        {'text': 'rsa encryption cipher decrypt', 'category': 'crypto'},
        {'text': 'base64 encoded hash password', 'category': 'crypto'},
        {'text': 'binary buffer overflow exploit', 'category': 'pwn'},
        {'text': 'shellcode rop chain stack', 'category': 'pwn'},
        {'text': 'reverse engineering decompile', 'category': 'reversing'},
        {'text': 'binary analysis disassemble', 'category': 'reversing'},
        {'text': 'image steganography hidden data', 'category': 'forensics'},
        {'text': 'pcap network traffic analysis', 'category': 'forensics'},
        {'text': 'osint social media username', 'category': 'osint'},
        {'text': 'google dork search intelligence', 'category': 'osint'},
    ]


if __name__ == '__main__':
    # Example usage
    trainer = ChallengeClassifierTrainer()
    
    # Create sample data
    data = create_sample_training_data()
    
    # Train
    trainer.train(data)
    
    # Save
    trainer.save_model('models/classifier.pkl')
    
    # Test prediction
    category, confidence = trainer.predict('web server sql injection')
    print(f"Predicted: {category} (confidence: {confidence:.2%})")
