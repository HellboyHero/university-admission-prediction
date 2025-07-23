from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from django.conf import settings
from .serializers import (
    UserSerializer, UserProfileSerializer, 
    CollegeSerializer, AdmissionPredictionSerializer,
    CollegeComparisonSerializer
)
from .models import UserProfile, College, AdmissionPrediction
from .permissions import IsOwnerOrReadOnly
import sys
import os

# Add the parent directory to sys.path to help with imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from model import AdmissionPredictor
except ImportError as e:
    raise ImportError(f"Could not import AdmissionPredictor: {str(e)}. Please ensure model.py is in the correct location.")

from django_filters.rest_framework import DjangoFilterBackend
from logging import getLogger
import traceback

logger = getLogger(__name__)

class PredictionError(APIException):
    status_code = 500
    default_detail = 'A server error occurred during prediction.'
    default_code = 'prediction_error'

class ServiceUnavailableError(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing user profiles.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__username', 'user__email']
    filterset_fields = ['research_experience']

    def get_queryset(self):
        """Get queryset for user profiles."""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new user profile."""
        try:
            if UserProfile.objects.filter(user=self.request.user).exists():
                raise ValidationError("Profile already exists for this user")
            serializer.save(user=self.request.user)
        except ValidationError as e:
            logger.error(f"Validation error creating profile: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating profile: {str(e)}\n{traceback.format_exc()}")
            raise PredictionError(detail=str(e))

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile."""
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "Could not retrieve profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['put'])
    def update_me(self, request):
        """Update the current user's profile."""
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except ValidationError as e:
            logger.error(f"Validation error updating profile: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "Could not update profile"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CollegeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and comparing colleges.
    """
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'country', 'ranking_range']
    search_fields = ['name', 'description', 'country']
    ordering_fields = ['name', 'ranking', 'acceptance_rate', 'created_at']
    ordering = ['ranking']

    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        """Get serializer context with request."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def compare(self, request, pk=None):
        """Compare two or more colleges."""
        try:
            # Validate input data
            serializer = CollegeComparisonSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Get base college
            base_college = self.get_object()
            college_ids = serializer.validated_data['college_ids']
            
            # Ensure base college is not in comparison list
            if base_college.id in college_ids:
                college_ids.remove(base_college.id)
            
            if not college_ids:
                return Response(
                    {"error": "Please provide at least one college to compare with"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get comparison colleges
            colleges = College.objects.filter(id__in=college_ids)
            if len(colleges) != len(college_ids):
                missing_ids = set(college_ids) - set(colleges.values_list('id', flat=True))
                return Response(
                    {"error": f"Invalid college IDs: {', '.join(map(str, missing_ids))}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare comparison data
            comparison_data = {
                'base_college': CollegeSerializer(base_college, context=self.get_serializer_context()).data,
                'compared_colleges': CollegeSerializer(colleges, many=True, context=self.get_serializer_context()).data,
                'comparison_metrics': self._calculate_comparison_metrics(base_college, colleges)
            }
            
            return Response(comparison_data)
            
        except ValidationError as e:
            logger.error(f"Validation error in college comparison: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in college comparison: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "An error occurred while comparing colleges"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_comparison_metrics(self, base_college, comparison_colleges):
        """Calculate comparison metrics between colleges."""
        metrics = {
            'ranking_difference': [],
            'acceptance_rate_difference': [],
            'cost_difference': [],
            'average_scores': {
                'gre_difference': [],
                'toefl_difference': []
            }
        }
        
        for college in comparison_colleges:
            metrics['ranking_difference'].append(college.ranking - base_college.ranking)
            metrics['acceptance_rate_difference'].append(
                college.acceptance_rate - base_college.acceptance_rate
            )
            metrics['cost_difference'].append(
                getattr(college, 'tuition_fee', 0) - getattr(base_college, 'tuition_fee', 0)
            )
            metrics['average_scores']['gre_difference'].append(
                getattr(college, 'average_gre', 0) - getattr(base_college, 'average_gre', 0)
            )
            metrics['average_scores']['toefl_difference'].append(
                getattr(college, 'average_toefl', 0) - getattr(base_college, 'average_toefl', 0)
            )
        
        return metrics

    @action(detail=True, methods=['post'])
    def toggle_save(self, request, pk=None):
        """Toggle save/unsave college for current user."""
        try:
            college = self.get_object()
            user = request.user
            
            if college.saved_by.filter(id=user.id).exists():
                college.saved_by.remove(user)
                saved = False
            else:
                college.saved_by.add(user)
                saved = True
            
            return Response({
                'saved': saved,
                'total_saves': college.saved_by.count()
            })
        except Exception as e:
            logger.error(f"Error toggling college save: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "Could not update college save status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def saved(self, request):
        """Get all colleges saved by the current user."""
        try:
            saved_colleges = College.objects.filter(saved_by=request.user)
            page = self.paginate_queryset(saved_colleges)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(saved_colleges, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving saved colleges: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "Could not retrieve saved colleges"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdmissionPredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and managing admission predictions.
    """
    serializer_class = AdmissionPredictionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['research']
    ordering_fields = ['created_at', 'prediction_probability']
    ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.predictor = AdmissionPredictor()
        except Exception as e:
            logger.error(f"Error initializing predictor: {str(e)}\n{traceback.format_exc()}")
            self.predictor = None

    def get_queryset(self):
        """Get queryset filtered by user."""
        if self.request.user.is_staff:
            return AdmissionPrediction.objects.all()
        return AdmissionPrediction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new prediction."""
        if not self.predictor:
            raise ServiceUnavailableError(detail="Prediction service is not available")

        try:
            # Get prediction from the model
            features = serializer.validated_data
            prediction_result = self.predictor.predict_admission(features)
            
            # Save prediction with user
            instance = serializer.save(
                user=self.request.user,
                prediction_probability=prediction_result['probability']
            )
            
            # Update user profile with latest scores if requested
            if serializer.validated_data.get('update_profile', False):
                profile = self.request.user.userprofile
                profile.gre_score = features.get('gre_score', profile.gre_score)
                profile.toefl_score = features.get('toefl_score', profile.toefl_score)
                profile.cgpa = features.get('cgpa', profile.cgpa)
                profile.research_experience = features.get('research', profile.research_experience)
                profile.save()
            
            return instance
            
        except ValidationError as e:
            logger.error(f"Validation error in prediction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}\n{traceback.format_exc()}")
            raise PredictionError(detail=str(e))

    @action(detail=False, methods=['post'])
    def batch_predict(self, request):
        """Handle batch predictions."""
        if not self.predictor:
            raise ServiceUnavailableError(detail="Prediction service is not available")

        try:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            
            # Get predictions for all instances
            predictions = self.predictor.batch_predict(serializer.validated_data)
            
            # Save all predictions
            instances = []
            for data, pred in zip(serializer.validated_data, predictions):
                instances.append(AdmissionPrediction(
                    user=request.user,
                    prediction_probability=pred['probability'],
                    **data
                ))
            
            # Use bulk create for efficiency
            created_predictions = AdmissionPrediction.objects.bulk_create(instances)
            
            # Return the predictions with additional metadata
            response_data = []
            for pred, instance in zip(predictions, created_predictions):
                pred_data = {
                    'id': instance.id,
                    'prediction_probability': pred['probability'],
                    'confidence': pred.get('confidence', None),
                    'features_importance': pred.get('features_importance', None),
                    'created_at': instance.created_at.isoformat()
                }
                response_data.append(pred_data)
            
            return Response(response_data)
            
        except ValidationError as e:
            logger.error(f"Validation error in batch prediction: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in batch prediction: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": f"Batch prediction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get prediction statistics for the current user."""
        try:
            predictions = self.get_queryset()
            stats_data = {
                'total_predictions': predictions.count(),
                'average_probability': predictions.aggregate(Avg('prediction_probability'))['prediction_probability__avg'],
                'high_chance_count': predictions.filter(prediction_probability__gte=0.7).count(),
                'medium_chance_count': predictions.filter(prediction_probability__range=(0.4, 0.7)).count(),
                'low_chance_count': predictions.filter(prediction_probability__lt=0.4).count(),
            }
            return Response(stats_data)
        except Exception as e:
            logger.error(f"Error retrieving prediction stats: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"error": "Could not retrieve prediction statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 