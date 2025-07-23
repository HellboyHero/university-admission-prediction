from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import College, AdmissionPrediction
from django.shortcuts import get_object_or_404

@login_required
@require_http_methods(["GET"])
def search_colleges(request):
    """API endpoint for searching colleges with filters"""
    query = request.GET.get('query', '')
    location = request.GET.get('location', '')
    min_acceptance = request.GET.get('min_acceptance')
    max_acceptance = request.GET.get('max_acceptance')
    page = int(request.GET.get('page', 1))
    
    colleges = College.objects.all()
    
    # Apply filters
    if query:
        colleges = colleges.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if location:
        colleges = colleges.filter(location__icontains=location)
    
    if min_acceptance:
        colleges = colleges.filter(acceptance_rate__gte=float(min_acceptance))
    
    if max_acceptance:
        colleges = colleges.filter(acceptance_rate__lte=float(max_acceptance))
    
    # Paginate results
    paginator = Paginator(colleges, 10)
    page_obj = paginator.get_page(page)
    
    return JsonResponse({
        'colleges': [{
            'id': college.id,
            'name': college.name,
            'location': college.location,
            'acceptance_rate': college.acceptance_rate,
            'ranking': college.ranking,
            'is_saved': request.user in college.saved_by.all()
        } for college in page_obj],
        'has_next': page_obj.has_next(),
        'total_pages': paginator.num_pages,
        'current_page': page
    })

@login_required
@require_http_methods(["POST"])
def toggle_save_college(request, college_id):
    """API endpoint for saving/unsaving a college"""
    college = get_object_or_404(College, id=college_id)
    
    if request.user in college.saved_by.all():
        college.saved_by.remove(request.user)
        saved = False
    else:
        college.saved_by.add(request.user)
        saved = True
    
    return JsonResponse({
        'saved': saved,
        'college_id': college_id
    })

@login_required
@require_http_methods(["GET"])
def compare_colleges(request):
    """API endpoint for comparing colleges"""
    college_ids = request.GET.getlist('colleges[]')
    
    if not college_ids or len(college_ids) < 2:
        return JsonResponse({
            'error': 'Please select at least two colleges to compare'
        }, status=400)
    
    colleges = College.objects.filter(id__in=college_ids)
    
    return JsonResponse({
        'colleges': [{
            'id': college.id,
            'name': college.name,
            'location': college.location,
            'acceptance_rate': college.acceptance_rate,
            'ranking': college.ranking,
            'tuition': college.tuition,
            'student_faculty_ratio': college.student_faculty_ratio,
            'total_enrollment': college.total_enrollment,
            'average_gre': college.average_gre,
            'average_toefl': college.average_toefl
        } for college in colleges]
    })

@login_required
@require_http_methods(["GET"])
def get_admission_chances(request, college_id):
    """API endpoint for getting personalized admission chances"""
    college = get_object_or_404(College, id=college_id)
    user_predictions = AdmissionPrediction.objects.filter(
        user=request.user
    ).order_by('-created_at').first()
    
    if not user_predictions:
        return JsonResponse({
            'error': 'Please make a prediction first'
        }, status=400)
    
    # Calculate chances based on college requirements and user's scores
    gre_factor = min(1, user_predictions.gre_score / college.average_gre) * 0.4
    toefl_factor = min(1, user_predictions.toefl_score / college.average_toefl) * 0.3
    cgpa_factor = min(1, user_predictions.cgpa / 4.0) * 0.3
    
    chance = (gre_factor + toefl_factor + cgpa_factor) * 100
    
    return JsonResponse({
        'college_name': college.name,
        'chance_of_admission': round(chance, 2),
        'factors': {
            'gre_comparison': {
                'your_score': user_predictions.gre_score,
                'college_average': college.average_gre
            },
            'toefl_comparison': {
                'your_score': user_predictions.toefl_score,
                'college_average': college.average_toefl
            },
            'cgpa_comparison': {
                'your_cgpa': user_predictions.cgpa,
                'recommended_cgpa': 3.0
            }
        }
    })

@login_required
@require_http_methods(["GET"])
def get_saved_colleges(request):
    """API endpoint for getting user's saved colleges"""
    colleges = College.objects.filter(saved_by=request.user)
    
    return JsonResponse({
        'colleges': [{
            'id': college.id,
            'name': college.name,
            'location': college.location,
            'acceptance_rate': college.acceptance_rate,
            'ranking': college.ranking
        } for college in colleges]
    })
