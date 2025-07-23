from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import api_views
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Create schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="University Admission Prediction API",
        default_version='v1',
        description="API for predicting university admission chances",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@admissionpredictor.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Create router for API views
router = DefaultRouter()
router.register(r'profiles', api_views.UserProfileViewSet, basename='profile')
router.register(r'colleges', api_views.CollegeViewSet, basename='college')
router.register(r'predictions', api_views.AdmissionPredictionViewSet, basename='prediction')

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('predict/', views.predict, name='predict'),
    path('colleges/', views.college_list, name='college_list'),
    path('college/<int:college_id>/', views.college_detail, name='college_detail'),
    path('college/<int:college_id>/toggle-save/', views.toggle_save_college, name='toggle_save_college'),
    
    # Social Authentication
    path('social-auth/', include('social_django.urls', namespace='social')),
    
    # Password Reset URLs
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='predictor/auth/password_reset.html',
            email_template_name='predictor/auth/password_reset_email.html',
            subject_template_name='predictor/auth/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='predictor/auth/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='predictor/auth/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='predictor/auth/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
