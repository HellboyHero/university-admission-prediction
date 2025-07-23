from django.test import TestCase
from django.contrib.auth.models import User
from predictor.models import College, AdmissionPrediction, UserProfile

class CollegeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.college = College.objects.create(
            name='Test University',
            location='Test Location',
            description='Test Description',
            acceptance_rate=50.0,
            ranking=100,
            tuition=50000,
            student_faculty_ratio=10,
            total_enrollment=20000,
            average_gre=320,
            average_toefl=100,
            website='http://test.edu'
        )

    def test_college_creation(self):
        self.assertEqual(self.college.name, 'Test University')
        self.assertEqual(self.college.location, 'Test Location')
        self.assertEqual(self.college.acceptance_rate, 50.0)

    def test_college_str_method(self):
        self.assertEqual(str(self.college), 'Test University')

    def test_save_college(self):
        self.college.saved_by.add(self.user)
        self.assertIn(self.user, self.college.saved_by.all())

class AdmissionPredictionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.prediction = AdmissionPrediction.objects.create(
            user=self.user,
            gre_score=320,
            toefl_score=105,
            cgpa=3.8,
            research_experience=True
        )

    def test_prediction_creation(self):
        self.assertEqual(self.prediction.gre_score, 320)
        self.assertEqual(self.prediction.toefl_score, 105)
        self.assertEqual(self.prediction.cgpa, 3.8)
        self.assertTrue(self.prediction.research_experience)

    def test_prediction_str_method(self):
        expected_str = f'Prediction for {self.user.username}'
        self.assertEqual(str(self.prediction), expected_str)

    def test_prediction_chance_calculation(self):
        chance = self.prediction.calculate_chance()
        self.assertIsInstance(chance, float)
        self.assertTrue(0 <= chance <= 100)

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.profile = UserProfile.objects.get(user=self.user)  # Profile created by signal

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.bio, '')
        self.assertIsNone(self.profile.avatar)

    def test_profile_str_method(self):
        expected_str = f'{self.user.username}\'s Profile'
        self.assertEqual(str(self.profile), expected_str)

    def test_profile_update(self):
        self.profile.bio = 'Test bio'
        self.profile.location = 'Test location'
        self.profile.save()
        
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, 'Test bio')
        self.assertEqual(updated_profile.location, 'Test location')
