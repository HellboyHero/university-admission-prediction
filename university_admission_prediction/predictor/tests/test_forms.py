from django.test import TestCase
from django.contrib.auth.models import User
from predictor.forms import (
    UserRegistrationForm,
    UserLoginForm,
    PredictionForm,
    UserUpdateForm,
    ProfileUpdateForm
)

class UserRegistrationFormTests(TestCase):
    def test_valid_registration_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_registration_form(self):
        # Test with mismatched passwords
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

        # Test with invalid email
        form_data = {
            'username': 'testuser',
            'email': 'invalid_email',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class UserLoginFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )

    def test_valid_login_form(self):
        form_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_login_form(self):
        # Test with wrong password
        form_data = {
            'username': 'testuser',
            'password': 'WrongPass123!'
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Test with non-existent user
        form_data = {
            'username': 'nonexistentuser',
            'password': 'TestPass123!'
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())

class PredictionFormTests(TestCase):
    def test_valid_prediction_form(self):
        form_data = {
            'gre_score': 320,
            'toefl_score': 105,
            'cgpa': 3.8,
            'research_experience': True
        }
        form = PredictionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_prediction_form(self):
        # Test with GRE score out of range
        form_data = {
            'gre_score': 350,  # Max is 340
            'toefl_score': 105,
            'cgpa': 3.8,
            'research_experience': True
        }
        form = PredictionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('gre_score', form.errors)

        # Test with TOEFL score out of range
        form_data = {
            'gre_score': 320,
            'toefl_score': 150,  # Max is 120
            'cgpa': 3.8,
            'research_experience': True
        }
        form = PredictionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('toefl_score', form.errors)

        # Test with CGPA out of range
        form_data = {
            'gre_score': 320,
            'toefl_score': 105,
            'cgpa': 5.0,  # Max is 4.0
            'research_experience': True
        }
        form = PredictionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cgpa', form.errors)

class UserUpdateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_valid_user_update_form(self):
        form_data = {
            'username': 'newusername',
            'email': 'newemail@example.com'
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_user_update_form(self):
        # Test with invalid email
        form_data = {
            'username': 'newusername',
            'email': 'invalid_email'
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ProfileUpdateFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )

    def test_valid_profile_update_form(self):
        form_data = {
            'bio': 'Test bio',
            'location': 'Test location',
            'birth_date': '2000-01-01',
            'website': 'https://example.com'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid())

    def test_invalid_profile_update_form(self):
        # Test with invalid website URL
        form_data = {
            'bio': 'Test bio',
            'location': 'Test location',
            'birth_date': '2000-01-01',
            'website': 'invalid_url'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

        # Test with invalid date format
        form_data = {
            'bio': 'Test bio',
            'location': 'Test location',
            'birth_date': 'invalid_date',
            'website': 'https://example.com'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)
