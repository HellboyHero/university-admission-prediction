from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from django.conf import settings
import numpy as np
import os
import json
import logging

logger = logging.getLogger(__name__)

class VertexAIPredictor:
    def __init__(self):
        self.project_id = settings.VERTEX_AI_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        self.endpoint_id = settings.VERTEX_AI_ENDPOINT_ID
        
        # Initialize Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.location,
        )
        
        self.endpoint = aiplatform.Endpoint(self.endpoint_id)
    
    def preprocess_features(self, prediction_data):
        """
        Preprocess the input features for prediction
        """
        features = [
            prediction_data.gre_score / 340.0,  # Normalize GRE score
            prediction_data.toefl_score / 120.0,  # Normalize TOEFL score
            prediction_data.university_rating / 5.0,  # Normalize university rating
            prediction_data.sop / 5.0,  # Normalize SOP
            prediction_data.lor / 5.0,  # Normalize LOR
            prediction_data.cgpa / 10.0,  # Normalize CGPA
            1.0 if prediction_data.research else 0.0  # Convert research to binary
        ]
        return features

    def predict_admission_chance(self, prediction_data):
        """
        Make admission prediction using Vertex AI
        """
        try:
            # Preprocess features
            features = self.preprocess_features(prediction_data)
            
            # Prepare the instance for prediction
            instance = {
                "input_values": features
            }
            
            # Make prediction
            response = self.endpoint.predict([instance])
            
            # Extract prediction and confidence
            predictions = response.predictions[0]
            admission_chance = float(predictions['admission_chance'])
            confidence_score = float(predictions.get('confidence', 0.8))
            
            return {
                'success': True,
                'admission_chance': admission_chance,
                'confidence_score': confidence_score
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def batch_predict(self, instances):
        """
        Make batch predictions for multiple instances
        """
        try:
            response = self.endpoint.batch_predict(instances=instances)
            return response.predictions
        except Exception as e:
            logger.error(f"Batch prediction error: {str(e)}")
            return None
