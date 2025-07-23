from .models import AdmissionPrediction, College
from .ml.vertex_ai import VertexAIPredictor
from django.db.models import Q
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AdmissionPredictionService:
    def __init__(self):
        self.predictor = VertexAIPredictor()

    def create_prediction(self, data, user=None):
        """
        Create and process a new admission prediction
        """
        try:
            # Create prediction instance
            prediction = AdmissionPrediction.objects.create(
                user=user,
                gre_score=data['gre_score'],
                toefl_score=data['toefl_score'],
                university_rating=data['university_rating'],
                sop=data['sop'],
                lor=data['lor'],
                cgpa=data['cgpa'],
                research=data['research'],
                status='processing'
            )

            # Get prediction from Vertex AI
            result = self.predictor.predict_admission_chance(prediction)

            if result['success']:
                prediction.admission_chance = result['admission_chance']
                prediction.confidence_score = result['confidence_score']
                prediction.status = 'completed'
                
                # Get recommended colleges
                colleges = prediction.get_recommended_colleges()
                prediction.recommended_colleges.set(colleges)
            else:
                prediction.status = 'error'
                logger.error(f"Prediction failed: {result.get('error')}")

            prediction.save()
            return prediction

        except Exception as e:
            logger.error(f"Error in create_prediction: {str(e)}")
            if prediction:
                prediction.status = 'error'
                prediction.save()
            raise

    def get_prediction_details(self, prediction_id, user=None):
        """
        Get detailed prediction results including recommended colleges
        """
        query = Q(id=prediction_id)
        if user and not user.is_staff:
            query &= Q(user=user)
            
        prediction = AdmissionPrediction.objects.filter(query).first()
        if not prediction:
            return None

        return {
            'prediction': prediction,
            'recommended_colleges': prediction.recommended_colleges.all(),
            'similar_predictions': self.get_similar_predictions(prediction)
        }

    def get_similar_predictions(self, prediction, limit=3):
        """
        Get similar predictions based on scores
        """
        return AdmissionPrediction.objects.filter(
            status='completed',
            gre_score__range=(prediction.gre_score - 10, prediction.gre_score + 10),
            cgpa__range=(prediction.cgpa - 0.5, prediction.cgpa + 0.5)
        ).exclude(id=prediction.id)[:limit]
