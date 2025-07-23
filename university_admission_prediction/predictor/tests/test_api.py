from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.models import College, AdmissionPrediction, UserProfile
import json
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

class APITests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test college
        self.college = College.objects.create(
            name='Test University',
            country='USA',
            ranking=50,
            acceptance_rate=15.5
        )
        
        # Create test profile
        self.profile = UserProfile.objects.create(
            user=self.user,
            gre_score=315,
            toefl_score=105,
            cgpa=8.5,
            research_experience=True
        )

    def test_get_profile(self):
        """Test retrieving user profile."""
        url = reverse('profile-detail', args=[self.profile.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_create_prediction(self):
        """Test creating a new prediction."""
        url = reverse('prediction-list')
        data = {
            'gre_score': 320,
            'toefl_score': 110,
            'university_rating': 4,
            'sop': 4.5,
            'lor': 4.0,
            'cgpa': 9.0,
            'research': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('prediction_probability', response.data)

    def test_college_comparison(self):
        """Test college comparison feature."""
        # Create another college for comparison
        college2 = College.objects.create(
            name='Another University',
            country='UK',
            ranking=75,
            acceptance_rate=20.0
        )
        
        url = reverse('college-compare', args=[self.college.id])
        response = self.client.post(url, {'college_ids': [college2.id]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['compared_colleges']), 1)

    def test_batch_prediction(self):
        """Test batch prediction functionality."""
        url = reverse('prediction-batch-predict')
        data = [
            {
                'gre_score': 320,
                'toefl_score': 110,
                'university_rating': 4,
                'sop': 4.5,
                'lor': 4.0,
                'cgpa': 9.0,
                'research': 1
            },
            {
                'gre_score': 310,
                'toefl_score': 105,
                'university_rating': 3,
                'sop': 4.0,
                'lor': 3.5,
                'cgpa': 8.5,
                'research': 0
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_colleges_api(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('api_search_colleges'), {
            'query': 'Test',
            'location': 'Location',
            'min_acceptance': 40,
            'max_acceptance': 60
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['colleges']), 1)
        self.assertEqual(data['colleges'][0]['name'], 'Test University')

    def test_toggle_save_college_api(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('api_toggle_save_college', args=[self.college.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['saved'])
        
        # Test unsaving
        response = self.client.post(reverse('api_toggle_save_college', args=[self.college.id]))
        data = json.loads(response.content)
        self.assertFalse(data['saved'])

    def test_compare_colleges_api(self):
        self.client.login(username='testuser', password='TestPass123!')
        college2 = College.objects.create(
            name='Another University',
            location='Another Location',
            acceptance_rate=60.0,
            ranking=150,
            average_gre=310,
            average_toefl=95
        )
        
        response = self.client.get(reverse('api_compare_colleges'), {
            'colleges[]': [self.college.id, college2.id]
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['colleges']), 2)
        self.assertEqual(data['colleges'][0]['name'], 'Test University')
        self.assertEqual(data['colleges'][1]['name'], 'Another University')

    def test_get_admission_chances_api(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('api_get_admission_chances', args=[self.college.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('chance_of_admission', data)
        self.assertIn('factors', data)

    def test_get_saved_colleges_api(self):
        self.client.login(username='testuser', password='TestPass123!')
        self.college.saved_by.add(self.user)
        
        response = self.client.get(reverse('api_get_saved_colleges'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['colleges']), 1)
        self.assertEqual(data['colleges'][0]['name'], 'Test University')
