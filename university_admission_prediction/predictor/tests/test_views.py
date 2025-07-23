from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from predictor.models import College, AdmissionPrediction, UserProfile

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_register_view(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='testuser').exists())

    def test_login_view(self):
        # Create a user first
        User.objects.create_user(username='testuser', password='TestPass123!')
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

class CollegeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.college = College.objects.create(
            name='Test University',
            location='Test Location',
            acceptance_rate=50.0,
            ranking=100
        )

    def test_college_list_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('college_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictor/college_list.html')
        self.assertContains(response, 'Test University')

    def test_college_detail_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('college_detail', args=[self.college.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictor/college_detail.html')
        self.assertContains(response, 'Test University')

class PredictionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.prediction_data = {
            'gre_score': 320,
            'toefl_score': 105,
            'cgpa': 3.8,
            'research_experience': 1
        }

    def test_prediction_create_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.post(reverse('predict'), self.prediction_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdmissionPrediction.objects.filter(user=self.user).exists())

    def test_prediction_result_view(self):
        self.client.login(username='testuser', password='TestPass123!')
        prediction = AdmissionPrediction.objects.create(
            user=self.user,
            gre_score=320,
            toefl_score=105,
            cgpa=3.8,
            research_experience=True
        )
        response = self.client.get(reverse('prediction_result', args=[prediction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictor/prediction_result.html')
