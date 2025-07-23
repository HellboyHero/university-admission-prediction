from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import College, AdmissionPrediction, UserProfile
from rest_framework import permissions

def create_default_groups():
    """Create default user groups with appropriate permissions"""
    
    # Create content types if they don't exist
    college_ct = ContentType.objects.get_for_model(College)
    prediction_ct = ContentType.objects.get_for_model(AdmissionPrediction)
    profile_ct = ContentType.objects.get_for_model(UserProfile)
    
    # Create or get groups
    student_group, _ = Group.objects.get_or_create(name='Student')
    counselor_group, _ = Group.objects.get_or_create(name='Counselor')
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    
    # Define permissions for each model
    college_permissions = {
        'view_college': 'Can view college',
        'save_college': 'Can save college to profile',
        'compare_colleges': 'Can compare colleges',
    }
    
    prediction_permissions = {
        'add_admissionprediction': 'Can add admission prediction',
        'view_admissionprediction': 'Can view admission prediction',
        'change_admissionprediction': 'Can change admission prediction',
        'delete_admissionprediction': 'Can delete admission prediction',
    }
    
    profile_permissions = {
        'view_userprofile': 'Can view user profile',
        'change_userprofile': 'Can change user profile',
    }
    
    # Create permissions if they don't exist
    for codename, name in college_permissions.items():
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=college_ct,
        )
    
    for codename, name in prediction_permissions.items():
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=prediction_ct,
        )
    
    for codename, name in profile_permissions.items():
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=profile_ct,
        )
    
    # Assign permissions to groups
    student_permissions = [
        'view_college',
        'save_college',
        'compare_colleges',
        'add_admissionprediction',
        'view_admissionprediction',
        'change_admissionprediction',
        'delete_admissionprediction',
        'view_userprofile',
        'change_userprofile',
    ]
    
    counselor_permissions = student_permissions + [
        'view_all_predictions',
        'add_college_review',
    ]
    
    admin_permissions = counselor_permissions + [
        'add_college',
        'change_college',
        'delete_college',
        'manage_users',
    ]
    
    # Clear existing permissions
    student_group.permissions.clear()
    counselor_group.permissions.clear()
    admin_group.permissions.clear()
    
    # Add permissions to groups
    for perm in Permission.objects.filter(codename__in=student_permissions):
        student_group.permissions.add(perm)
    
    for perm in Permission.objects.filter(codename__in=counselor_permissions):
        counselor_group.permissions.add(perm)
    
    for perm in Permission.objects.filter(codename__in=admin_permissions):
        admin_group.permissions.add(perm)

def assign_default_group(user):
    """Assign default group to new users"""
    student_group = Group.objects.get(name='Student')
    user.groups.add(student_group)

def has_college_permission(user, college, permission):
    """Check if user has specific permission for a college"""
    if user.is_superuser:
        return True
    
    if permission == 'view':
        return user.has_perm('predictor.view_college')
    elif permission == 'save':
        return user.has_perm('predictor.save_college')
    elif permission == 'compare':
        return user.has_perm('predictor.compare_colleges')
    elif permission in ['add', 'change', 'delete']:
        return user.has_perm(f'predictor.{permission}_college')
    
    return False

def has_prediction_permission(user, prediction, permission):
    """Check if user has specific permission for a prediction"""
    if user.is_superuser:
        return True
    
    # Users can always view/edit their own predictions
    if prediction.user == user:
        return True
    
    if permission == 'view':
        return user.has_perm('predictor.view_admissionprediction')
    elif permission in ['add', 'change', 'delete']:
        return user.has_perm(f'predictor.{permission}_admissionprediction')
    
    return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user
