from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PredictionForm, UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm
from .models import College, AdmissionPrediction, UserProfile, AdmissionData
from django.core.paginator import Paginator
from django.db.models import Q
from .ml_predictor import MLPredictor

def home(request):
    return render(request, 'predictor/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'predictor/auth/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'predictor/auth/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)

    predictions = AdmissionPrediction.objects.filter(user=request.user).order_by('-created_at')[:5]
    saved_colleges = College.objects.filter(saved_by=request.user)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'predictions': predictions,
        'saved_colleges': saved_colleges
    }
    return render(request, 'predictor/profile.html', context)

@login_required
def predict(request):
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.save()
            
            # Get college recommendations based on scores
            colleges = College.objects.filter(
                min_gre_score__lte=prediction.gre_score,
                min_toefl_score__lte=prediction.toefl_score,
                min_cgpa__lte=prediction.cgpa
            ).order_by('ranking')[:5]
            
            # Use ML model for prediction
            predictor = MLPredictor()
            
            # Calculate chances for each recommended college
            college_predictions = []
            for college in colleges:
                data = {
                    'gre_score': prediction.gre_score,
                    'toefl_score': prediction.toefl_score,
                    'cgpa': prediction.cgpa,
                    'research_experience': prediction.research_experience,
                    'sop': prediction.sop,
                    'lor': prediction.lor,
                    'university_ranking': college.ranking,
                    'university_acceptance_rate': college.acceptance_rate
                }
                features = predictor.prepare_features(data)
                chance = predictor.predict_probability(features)
                college_predictions.append({
                    'college': college,
                    'chance': chance
                })
            
            # Sort colleges by predicted chance
            college_predictions.sort(key=lambda x: x['chance'], reverse=True)
            
            context = {
                'prediction': prediction,
                'recommended_colleges': college_predictions
            }
            return render(request, 'predictor/prediction_result.html', context)
    else:
        form = PredictionForm()
    return render(request, 'predictor/prediction_form.html', {'form': form})

@login_required
def college_list(request):
    query = request.GET.get('q', '')
    country = request.GET.get('country', '')
    acceptance_rate_filter = request.GET.get('acceptance_rate', '')
    
    # Get all unique countries for the filter dropdown
    countries = College.objects.values_list('country', flat=True).distinct().order_by('country')
    
    # Base queryset
    colleges = College.objects.all().order_by('country', 'ranking')
    
    # Apply filters
    if query:
        colleges = colleges.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if country:
        colleges = colleges.filter(country__iexact=country)
    
    # Handle acceptance rate filter
    if acceptance_rate_filter:
        if acceptance_rate_filter == 'very_selective':
            colleges = colleges.filter(acceptance_rate__lt=10)
        elif acceptance_rate_filter == 'selective':
            colleges = colleges.filter(acceptance_rate__gte=10, acceptance_rate__lt=20)
        elif acceptance_rate_filter == 'moderate':
            colleges = colleges.filter(acceptance_rate__gte=20, acceptance_rate__lt=30)
    
    # Group colleges by country
    colleges_by_country = {}
    for college in colleges:
        if college.country not in colleges_by_country:
            colleges_by_country[college.country] = []
        colleges_by_country[college.country].append(college)
    
    context = {
        'colleges_by_country': colleges_by_country,
        'countries': countries,
        'selected_country': country,
        'acceptance_rate_filter': acceptance_rate_filter,
        'search_query': query
    }
    
    return render(request, 'predictor/college_list.html', context)

@login_required
def college_detail(request, college_id):
    college = get_object_or_404(College, id=college_id)
    is_saved = request.user in college.saved_by.all()
    
    # Get user's latest prediction
    latest_prediction = AdmissionPrediction.objects.filter(
        user=request.user
    ).order_by('-created_at').first()
    
    # Calculate admission chance if prediction exists
    admission_chance = None
    if latest_prediction:
        # Handle zero values in average scores
        gre_factor = min(1, latest_prediction.gre_score / max(1, college.average_gre)) * 0.4
        toefl_factor = min(1, latest_prediction.toefl_score / max(1, college.average_toefl)) * 0.3
        cgpa_factor = min(1, latest_prediction.cgpa / 4.0) * 0.3
        admission_chance = round((gre_factor + toefl_factor + cgpa_factor) * 100, 2)
    
    context = {
        'college': college,
        'is_saved': is_saved,
        'admission_chance': admission_chance,
        'latest_prediction': latest_prediction
    }
    return render(request, 'predictor/college_detail.html', context)

@login_required
def toggle_save_college(request, college_id):
    college = get_object_or_404(College, id=college_id)
    
    if request.user in college.saved_by.all():
        college.saved_by.remove(request.user)
        messages.success(request, f'Removed {college.name} from saved colleges.')
    else:
        college.saved_by.add(request.user)
        messages.success(request, f'Added {college.name} to saved colleges.')
    
    return redirect('college_detail', college_id=college_id)
