import joblib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline

  

class SVMSentiment:
    def __init__(self):
        # Initialize the vectorizer and TF-IDF components
        self.vectorizer = CountVectorizer()
        self.tfidf = TfidfTransformer()

        # Initialize the SGDClassifier
        self.sgd = SGDClassifier(
            loss='hinge',
            penalty='l2',
            alpha=1e-3,
            random_state=42,
            max_iter=100,
            learning_rate='optimal',
            tol=None,
        )

    def fit(self, X_train, y_train):
        # Fit the vectorizer and transform X_train
        X_train_vec = self.vectorizer.fit_transform(X_train)
        # Apply TF-IDF transformation
        X_train_tfidf = self.tfidf.fit_transform(X_train_vec)
        # Fit the SGD classifier
        self.sgd.fit(X_train_tfidf, y_train)

        # Calibrate the classifier on the training data with 'prefit'
        self.calibrated_sgd = CalibratedClassifierCV(self.sgd, cv='prefit')
        self.calibrated_sgd.fit(X_train_tfidf, y_train)

    def predict(self, X):
        # Transform input using the existing vectorizer and TF-IDF
        X_vec = self.vectorizer.transform(X)
        X_tfidf = self.tfidf.transform(X_vec)
        # Predict with the calibrated classifier
        return self.calibrated_sgd.predict(X_tfidf)

    def predict_proba(self, X):
        # Transform input using the existing vectorizer and TF-IDF
        X_vec = self.vectorizer.transform(X)
        X_tfidf = self.tfidf.transform(X_vec)
        # Predict probabilities with the calibrated classifier
        return self.calibrated_sgd.predict_proba(X_tfidf)

    def predict_text(self, text: str) -> str:
        # Ensure the calibrated_sgd is fit
        if not hasattr(self, 'calibrated_sgd'):
            raise ValueError("Model must be trained before predicting.")
        # Transform input text
        X_vec = self.vectorizer.transform([text])
        X_tfidf = self.tfidf.transform(X_vec)
        # Predict class
        predicted_class = self.calibrated_sgd.predict(X_tfidf)[0]
        # Predict probabilities
        probabilities = self.calibrated_sgd.predict_proba(X_tfidf)[0]

         # Assuming the 'Positive' class is the last one, adjust indices as necessary
        positive_probability = probabilities[-1]

        if positive_probability < 0.5:
           class_label = 'Negative'
        elif 0.5 <= positive_probability < 0.75:  # Adjust the 0.75 threshold as needed
          class_label = 'Neutral'
        else:
          class_label = 'Positive'

    # The sentiment score is the probability of being 'Positive'
        sentiment_score = positive_probability

        return class_label, sentiment_score


    def load_model(self, filepath):
        # Load the pre-trained model components
        loaded_model = joblib.load(filepath)
        self.vectorizer = loaded_model['vectorizer']
        self.tfidf = loaded_model['tfidf']
        self.calibrated_sgd = loaded_model['calibrated_sgd']