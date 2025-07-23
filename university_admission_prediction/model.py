from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.cloud import storage
import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib

class AdmissionPredictor:
    def __init__(self):
        """Initialize the AdmissionPredictor with a Random Forest model."""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self._initialize_model()

    def _initialize_model(self):
        """Initialize a basic model with some sample data if no trained model exists."""
        # Sample data for initial training
        sample_data = pd.DataFrame({
            'GRE Score': [337, 324, 316, 322, 314, 330, 321, 308, 302, 323],
            'TOEFL Score': [118, 107, 104, 110, 103, 115, 109, 101, 102, 108],
            'University Rating': [4, 4, 3, 3, 2, 5, 3, 2, 1, 4],
            'SOP': [4.5, 4.0, 3.0, 3.5, 2.0, 4.5, 3.0, 3.0, 2.0, 4.0],
            'LOR': [4.5, 4.5, 3.5, 2.5, 3.0, 3.0, 4.0, 4.0, 2.5, 3.0],
            'CGPA': [9.65, 8.87, 8.00, 8.67, 8.21, 9.34, 8.20, 7.90, 8.00, 8.60],
            'Research': [1, 1, 0, 1, 0, 1, 1, 0, 0, 1]
        })
        sample_target = pd.Series([0.92, 0.76, 0.72, 0.80, 0.65, 0.90, 0.75, 0.68, 0.50, 0.85])
        
        # Train the model with sample data
        X = sample_data.values
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, sample_target)

    def predict_admission(self, features):
        """
        Make prediction using the scikit-learn model.
        
        Args:
            features: Dictionary containing the input features
        Returns:
            dict: Prediction results including probability and confidence metrics
        """
        # Prepare the instance
        instance = self._prepare_instance(features)
        
        # Make prediction
        scaled_instance = self.scaler.transform([instance])
        probability = float(self.model.predict(scaled_instance)[0])
        
        # Get feature importances
        importance = self._get_feature_importance(features)
        
        result = {
            'probability': max(min(probability, 1.0), 0.0),  # Clip between 0 and 1
            'confidence': self._calculate_confidence(probability),
            'features_importance': importance
        }
        
        return result

    def batch_predict(self, instances):
        """
        Make batch predictions using the scikit-learn model.
        
        Args:
            instances: List of feature dictionaries
        Returns:
            list: List of prediction results
        """
        formatted_instances = [self._prepare_instance(inst) for inst in instances]
        scaled_instances = self.scaler.transform(formatted_instances)
        probabilities = self.model.predict(scaled_instances)
        
        return [self._process_prediction(prob, inst) for prob, inst in zip(probabilities, instances)]

    def _prepare_instance(self, features):
        """Prepare instance for prediction."""
        return [
            float(features.get('GRE Score', 0)),
            float(features.get('TOEFL Score', 0)),
            float(features.get('University Rating', 0)),
            float(features.get('SOP', 0)),
            float(features.get('LOR', 0)),
            float(features.get('CGPA', 0)),
            int(features.get('Research', 0))
        ]

    def _calculate_confidence(self, probability):
        """Calculate confidence score for the prediction."""
        # Simple confidence calculation based on distance from 0.5
        return min(max(abs(probability - 0.5) * 2, 0), 1)

    def _get_feature_importance(self, features):
        """Get feature importance based on the random forest model."""
        feature_names = ['GRE Score', 'TOEFL Score', 'University Rating', 
                        'SOP', 'LOR', 'CGPA', 'Research']
        importances = dict(zip(feature_names, self.model.feature_importances_))
        return importances

    def _process_prediction(self, probability, features):
        """Process a single prediction result."""
        probability = float(max(min(probability, 1.0), 0.0))  # Clip between 0 and 1
        return {
            'probability': probability,
            'confidence': self._calculate_confidence(probability),
            'features_importance': self._get_feature_importance(features)
        }
