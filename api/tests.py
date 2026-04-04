from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from capsules.models import Capsule

User = get_user_model()


class APITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.future_date = timezone.now() + timedelta(days=30)
        self.capsule = Capsule.objects.create(
            title='API Test Capsule',
            description='Test Description',
            creator=self.user,
            open_date=self.future_date,
            privacy='public'
        )

    def test_public_capsules_api(self):
        response = self.client.get(reverse('api:public_capsules'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_capsule_detail_api(self):
        response = self.client.get(reverse('api:capsule_detail', kwargs={'pk': self.capsule.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'API Test Capsule')

    def test_user_profile_api(self):
        response = self.client.get(reverse('api:user_profile', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')

    def test_user_stats_api(self):
        response = self.client.get(reverse('api:user_stats', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_capsules', data)
        self.assertIn('public_capsules', data)

    def test_my_capsules_api_requires_auth(self):
        response = self.client.get(reverse('api:my_capsules'))
        self.assertEqual(response.status_code, 403)  # Forbidden (not authenticated)

    def test_my_capsules_api_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('api:my_capsules'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
