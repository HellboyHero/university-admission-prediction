import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings

class MLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'admission_model.joblib')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'scaler.joblib')
        self._load_or_create_model()

    def _load_or_create_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        except:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()

    def prepare_features(self, data):
        features = np.array([
            data['gre_score'],
            data['toefl_score'],
            data['cgpa'],
            1 if data['research_experience'] else 0,
            data['sop'],
            data['lor'],
            data.get('university_ranking', 50),  # Default value if not provided
            data.get('university_acceptance_rate', 20)  # Default value if not provided
        ]).reshape(1, -1)
        return features

    def train(self, X, y):
        # Scale the features
        X_scaled = self.scaler.fit_transform(X)
        # Train the model
        self.model.fit(X_scaled, y)
        # Save the model and scaler
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

    def predict_probability(self, features):
        # Scale the features
        features_scaled = self.scaler.transform(features)
        # Get probability of admission
        proba = self.model.predict_proba(features_scaled)[0][1]
        return round(proba * 100, 2)  # Convert to percentage and round to 2 decimal places

# Create sample training data
def create_sample_data(n_samples=1000):
    np.random.seed(42)
    
    # Generate random features
    gre_scores = np.random.normal(315, 15, n_samples).clip(260, 340)
    toefl_scores = np.random.normal(100, 10, n_samples).clip(70, 120)
    cgpa = np.random.normal(3.5, 0.3, n_samples).clip(2.5, 4.0)
    research = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    sop = np.random.normal(4, 0.5, n_samples).clip(1, 5)
    lor = np.random.normal(4, 0.5, n_samples).clip(1, 5)
    rankings = np.random.randint(1, 100, n_samples)
    acceptance_rates = np.random.uniform(5, 30, n_samples)
    
    # Combine features
    X = np.column_stack([
        gre_scores, toefl_scores, cgpa, research, sop, lor, rankings, acceptance_rates
    ])
    
    # Generate target variable (admitted or not)
    # Higher scores and research experience increase chances of admission
    probabilities = (
        0.3 * (gre_scores - 260) / 80 +  # GRE contribution
        0.2 * (toefl_scores - 70) / 50 +  # TOEFL contribution
        0.2 * (cgpa - 2.5) / 1.5 +  # CGPA contribution
        0.15 * research +  # Research contribution
        0.075 * (sop - 1) / 4 +  # SOP contribution
        0.075 * (lor - 1) / 4  # LOR contribution
    )
    
    # Adjust probabilities based on university ranking and acceptance rate
    probabilities = probabilities * (1 - (rankings - 1) / 198)  # Lower rank = higher chance
    probabilities = probabilities * (acceptance_rates / 30)  # Higher acceptance rate = higher chance
    
    # Convert probabilities to binary outcomes
    y = (np.random.random(n_samples) < probabilities).astype(int)
    
    return X, y 