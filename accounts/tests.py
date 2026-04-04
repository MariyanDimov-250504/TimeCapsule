from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_method(self):
        user = User.objects.create_user(username='testuser', password='pass')
        self.assertEqual(str(user), 'testuser')

    def test_user_full_name_property(self):
        user = User.objects.create_user(
            username='testuser',
            first_name='John',
            last_name='Doe',
            password='pass'
        )
        self.assertEqual(user.full_name, 'John Doe')

        # Test with no first/last name
        user2 = User.objects.create_user(username='testuser2', password='pass')
        self.assertEqual(user2.full_name, 'testuser2')


class RegistrationFormTests(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_valid_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'bio': 'Test bio',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'existing',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200) # Check that form has error
        self.assertContains(response, 'A user with that username already exists.')

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Password123!',
            'password2': 'Different123!',
        })
        self.assertEqual(response.status_code, 200)
        # Check that error message appears in response
        self.assertContains(response, "The two password fields didn’t match.")

    def test_register_short_username(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'ab',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username must be at least 3 characters long.")

class LoginTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_valid_user(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_invalid_user(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page


class ProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            bio='Original bio'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('accounts:profile', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'testuser')

    def test_profile_edit_page_loads(self):
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit.html')

    def test_profile_edit_update(self):
        response = self.client.post(reverse('accounts:profile_edit'), {
            'username': 'testuser',  # Readonly but must be submitted
            'email': 'newemail@example.com',
            'bio': 'Updated bio',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.bio, 'Updated bio')
        self.assertEqual(self.user.first_name, 'John')

    def test_profile_edit_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
