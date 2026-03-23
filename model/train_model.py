"""
train_model.py  –  BlogVerse ML Training Script
Trains a simple TF-IDF + Logistic Regression model to classify
articles into categories. Saves the pipeline as model.pkl.

Usage:
    python model/train_model.py
"""

import os
import pickle

# ── Sample training data ────────────────────────────────────────
TRAINING_DATA = [
    ("Python Flask web development tutorial REST API",          "Technology"),
    ("JavaScript React components hooks state management",      "Technology"),
    ("Machine learning neural network deep learning AI",        "Technology"),
    ("Healthy eating habits balanced diet nutrition tips",      "Health"),
    ("Exercise workout fitness gym strength training",          "Health"),
    ("Mental health stress anxiety mindfulness meditation",     "Health"),
    ("Travel destinations Europe Asia backpacking itinerary",   "Travel"),
    ("Budget travel tips hostels flights cheap deals",          "Travel"),
    ("Business startup entrepreneurship funding venture",       "Business"),
    ("Marketing strategy social media brand growth",            "Business"),
    ("Science experiment physics chemistry biology research",   "Science"),
    ("Climate change environment sustainability ecosystem",     "Science"),
    ("Cooking recipes cuisine food preparation kitchen tips",   "Food"),
    ("Restaurant review fine dining street food culture",       "Food"),
    ("Book review literature fiction novel author writing",     "Education"),
    ("Online courses learning skills programming certification","Education"),
]

LABELS = [label for _, label in TRAINING_DATA]
TEXTS  = [text  for text,  _ in TRAINING_DATA]


def train():
    try:
        from sklearn.pipeline import Pipeline
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        import numpy as np

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ('clf',   LogisticRegression(max_iter=500, random_state=42)),
        ])

        pipeline.fit(TEXTS, LABELS)

        # Quick cross-val score
        scores = cross_val_score(pipeline, TEXTS, LABELS, cv=3, scoring='accuracy')
        print(f"Cross-val accuracy: {np.mean(scores):.2f} (+/- {np.std(scores):.2f})")

        model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(pipeline, f)
        print(f"Model saved to {model_path}")

    except ImportError:
        # sklearn not installed – save a lightweight mock
        print("scikit-learn not found. Saving a mock model for demo purposes.")
        _save_mock_model()


def _save_mock_model():
    """Saves a simple dict-based rule model when sklearn is unavailable."""
    RULES = {
        'technology': 'Technology', 'tech': 'Technology', 'python': 'Technology',
        'flask': 'Technology',    'javascript': 'Technology', 'ai': 'Technology',
        'health': 'Health',       'fitness': 'Health', 'diet': 'Health',
        'travel': 'Travel',       'trip': 'Travel',  'destination': 'Travel',
        'business': 'Business',   'startup': 'Business', 'marketing': 'Business',
        'science': 'Science',     'research': 'Science', 'climate': 'Science',
        'food': 'Food',           'recipe': 'Food', 'cooking': 'Food',
        'education': 'Education', 'learning': 'Education', 'course': 'Education',
    }

    class MockModel:
        def predict(self, texts):
            results = []
            for text in texts:
                text_lower = text.lower()
                predicted = 'Other'
                for keyword, category in RULES.items():
                    if keyword in text_lower:
                        predicted = category
                        break
                results.append(predicted)
            return results

    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(MockModel(), f)
    print(f"Mock model saved to {model_path}")


if __name__ == '__main__':
    train()
