from django.contrib import admin
from .models import College, AdmissionPrediction, UserProfile

# Register your models here.

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'ranking', 'acceptance_rate', 'average_gre', 'average_toefl', 'tuition')
    list_filter = ('location', 'ranking')
    search_fields = ('name', 'location', 'description')
    ordering = ('ranking',)

@admin.register(AdmissionPrediction)
class AdmissionPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'gre_score', 'toefl_score', 'cgpa', 'research_experience', 'created_at')
    list_filter = ('research_experience', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date', 'website')
    search_fields = ('user__username', 'user__email', 'location')
    list_filter = ('location',)
