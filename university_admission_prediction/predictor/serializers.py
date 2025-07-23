from rest_framework import serializers
from .models import College, AdmissionPrediction, UserProfile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class CollegeSerializer(serializers.ModelSerializer):
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = College
        fields = '__all__'

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.saved_by.all()
        return False

class AdmissionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionPrediction
        fields = ('gre_score', 'toefl_score', 'university_rating', 'sop', 'lor', 
                 'cgpa', 'research', 'prediction_probability', 'created_at')
        read_only_fields = ('prediction_probability', 'created_at')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'gre_score', 'toefl_score', 'cgpa', 'research_experience')
        read_only_fields = ('user',)

class CollegeComparisonSerializer(serializers.Serializer):
    college_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=5
    )
