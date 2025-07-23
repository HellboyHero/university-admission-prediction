from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import AdmissionPrediction, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

class PredictionForm(forms.ModelForm):
    gre_score = forms.IntegerField(
        validators=[MinValueValidator(260), MaxValueValidator(340)],
        help_text='Enter GRE score (260-340)'
    )
    toefl_score = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text='Enter TOEFL score (0-120)'
    )
    cgpa = forms.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)],
        help_text='Enter CGPA (0.0-4.0)'
    )
    research_experience = forms.ChoiceField(
        choices=[(True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
        help_text='Do you have research experience (publications, projects, etc.)?'
    )
    sop = forms.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text='Rate your Statement of Purpose (1.0-5.0)'
    )
    lor = forms.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)],
        help_text='Rate your Letter of Recommendation (1.0-5.0)'
    )

    class Meta:
        model = AdmissionPrediction
        fields = ['gre_score', 'toefl_score', 'cgpa', 'research_experience', 'sop', 'lor']

    def clean(self):
        cleaned_data = super().clean()
        gre_score = cleaned_data.get('gre_score')
        toefl_score = cleaned_data.get('toefl_score')
        cgpa = cleaned_data.get('cgpa')

        if gre_score and (gre_score < 260 or gre_score > 340):
            self.add_error('gre_score', 'GRE score must be between 260 and 340')

        if toefl_score and (toefl_score < 0 or toefl_score > 120):
            self.add_error('toefl_score', 'TOEFL score must be between 0 and 120')

        if cgpa and (cgpa < 0.0 or cgpa > 4.0):
            self.add_error('cgpa', 'CGPA must be between 0.0 and 4.0')

        # Convert research_experience string to boolean
        research = cleaned_data.get('research_experience')
        if research is not None:
            cleaned_data['research_experience'] = research == 'True'

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location', 'birth_date', 'website', 'interests']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'interests': forms.Textarea(attrs={'rows': 3})
        }
