import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_prediction.settings')
django.setup()

from predictor.models import College

# Sample college data
colleges = [
    {
        'name': 'Massachusetts Institute of Technology',
        'location': 'Cambridge, MA',
        'ranking': 1,
        'acceptance_rate': 7.3,
        'min_gre_score': 320,
        'min_toefl_score': 100,
        'min_cgpa': 8.5,
        'website': 'https://www.mit.edu'
    },
    {
        'name': 'Stanford University',
        'location': 'Stanford, CA',
        'ranking': 2,
        'acceptance_rate': 5.2,
        'min_gre_score': 325,
        'min_toefl_score': 100,
        'min_cgpa': 8.7,
        'website': 'https://www.stanford.edu'
    },
    {
        'name': 'University of California, Berkeley',
        'location': 'Berkeley, CA',
        'ranking': 3,
        'acceptance_rate': 17.5,
        'min_gre_score': 315,
        'min_toefl_score': 90,
        'min_cgpa': 8.0,
        'website': 'https://www.berkeley.edu'
    },
    {
        'name': 'Georgia Institute of Technology',
        'location': 'Atlanta, GA',
        'ranking': 4,
        'acceptance_rate': 21,
        'min_gre_score': 310,
        'min_toefl_score': 85,
        'min_cgpa': 7.5,
        'website': 'https://www.gatech.edu'
    },
    {
        'name': 'University of Illinois Urbana-Champaign',
        'location': 'Champaign, IL',
        'ranking': 5,
        'acceptance_rate': 45,
        'min_gre_score': 305,
        'min_toefl_score': 80,
        'min_cgpa': 7.0,
        'website': 'https://illinois.edu'
    },
    {
        'name': 'Purdue University',
        'location': 'West Lafayette, IN',
        'ranking': 6,
        'acceptance_rate': 60,
        'min_gre_score': 300,
        'min_toefl_score': 75,
        'min_cgpa': 6.5,
        'website': 'https://www.purdue.edu'
    }
]

def add_sample_colleges():
    # Clear existing colleges
    College.objects.all().delete()
    
    # Add new colleges
    for college_data in colleges:
        College.objects.create(**college_data)
    
    print("Sample colleges have been added successfully!")

if __name__ == '__main__':
    add_sample_colleges()
