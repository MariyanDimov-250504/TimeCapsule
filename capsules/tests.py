from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Capsule
from .forms import CapsuleForm

User = get_user_model()


class CapsuleModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass')
        self.future_date = timezone.now() + timedelta(days=30)

    def test_create_capsule(self):
        capsule = Capsule.objects.create(
            title='Test Capsule',
            description='Test Description',
            creator=self.user,
            open_date=self.future_date,
            privacy='private'
        )
        self.assertEqual(capsule.title, 'Test Capsule')
        self.assertEqual(capsule.creator, self.user)
        self.assertEqual(capsule.status, 'sealed')
        self.assertEqual(capsule.views_count, 0)

    def test_capsule_str_method(self):
        capsule = Capsule.objects.create(
            title='My Capsule',
            creator=self.user,
            open_date=self.future_date
        )
        expected = f"My Capsule - {self.user.username}"
        self.assertEqual(str(capsule), expected)

    def test_can_user_view_private(self):
        capsule = Capsule.objects.create(
            title='Private Capsule',
            creator=self.user,
            open_date=self.future_date,
            privacy='private'
        )
        # Creator can view
        self.assertTrue(capsule.can_user_view(self.user))

        # Other user cannot view
        other_user = User.objects.create_user(username='other', password='pass')
        self.assertFalse(capsule.can_user_view(other_user))

        # Anonymous cannot view
        self.assertFalse(capsule.can_user_view(None))

    def test_can_user_view_public(self):
        capsule = Capsule.objects.create(
            title='Public Capsule',
            creator=self.user,
            open_date=self.future_date,
            privacy='public'
        )
        # Creator can view
        self.assertTrue(capsule.can_user_view(self.user))

        # Other user can view
        other_user = User.objects.create_user(username='other', password='pass')
        self.assertTrue(capsule.can_user_view(other_user))

        # Anonymous can view
        self.assertTrue(capsule.can_user_view(None))

    def test_can_user_view_shared(self):
        other_user = User.objects.create_user(username='friend', password='pass')
        capsule = Capsule.objects.create(
            title='Shared Capsule',
            creator=self.user,
            open_date=self.future_date,
            privacy='shared'
        )
        capsule.allowed_users.add(other_user)

        # Creator can view
        self.assertTrue(capsule.can_user_view(self.user))

        # Allowed user can view
        self.assertTrue(capsule.can_user_view(other_user))

        # Non-allowed user cannot view
        stranger = User.objects.create_user(username='stranger', password='pass')
        self.assertFalse(capsule.can_user_view(stranger))

    def test_time_until_open_property(self):
        # Future capsule
        future = timezone.now() + timedelta(days=5, hours=3)
        capsule = Capsule.objects.create(
            title='Future',
            creator=self.user,
            open_date=future
        )
        self.assertIn('day', capsule.time_until_open)

        # Past capsule (ready to open)
        past = timezone.now() - timedelta(days=1)
        capsule2 = Capsule.objects.create(
            title='Past',
            creator=self.user,
            open_date=past
        )
        self.assertEqual(capsule2.time_until_open, "Ready to open!")

    def test_is_openable_property(self):
        # Future capsule - not openable
        future = timezone.now() + timedelta(days=30)
        capsule = Capsule.objects.create(
            title='Future',
            creator=self.user,
            open_date=future
        )
        self.assertFalse(capsule.is_openable)

        # Past capsule - openable
        past = timezone.now() - timedelta(days=1)
        capsule2 = Capsule.objects.create(
            title='Past',
            creator=self.user,
            open_date=past
        )
        self.assertTrue(capsule2.is_openable)


class CapsuleFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass')
        self.future_date = timezone.now() + timedelta(days=30)

    def test_valid_capsule_form(self):
        form_data = {
            'title': 'Test Capsule',
            'description': 'Test Description',
            'open_date': self.future_date.strftime('%Y-%m-%d %H:%M'),
            'privacy': 'private',
        }
        form = CapsuleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_open_date_past(self):
        past_date = timezone.now() - timedelta(days=1)
        form_data = {
            'title': 'Test Capsule',
            'open_date': past_date.strftime('%Y-%m-%d %H:%M'),
            'privacy': 'private',
        }
        form = CapsuleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('open_date', form.errors)


class CapsuleViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='pass')
        self.future_date = timezone.now() + timedelta(days=30)
        self.capsule = Capsule.objects.create(
            title='Test Capsule',
            creator=self.user,
            open_date=self.future_date,
            privacy='public'
        )

    def test_public_capsules_list(self):
        response = self.client.get(reverse('capsules:public'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'capsules/capsule_list.html')
        self.assertContains(response, 'Test Capsule')

    def test_capsule_detail_view(self):
        response = self.client.get(reverse('capsules:detail', kwargs={'pk': self.capsule.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'capsules/capsule_detail.html')
        self.assertContains(response, 'Test Capsule')

    def test_create_capsule_requires_login(self):
        response = self.client.get(reverse('capsules:create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_create_capsule_logged_in(self):
        self.client.login(username='creator', password='pass')
        future_date = timezone.now() + timedelta(days=30)
        response = self.client.post(reverse('capsules:create'), {
            'title': 'New Capsule',
            'description': 'New Description',
            'open_date': future_date.strftime('%Y-%m-%d %H:%M'),
            'privacy': 'private',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Capsule.objects.filter(title='New Capsule').exists())

    def test_my_capsules_page(self):
        self.client.login(username='creator', password='pass')
        response = self.client.get(reverse('capsules:my_capsules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'capsules/my_capsules.html')
        self.assertContains(response, 'Test Capsule')

    def test_delete_capsule_confirmation(self):
        self.client.login(username='creator', password='pass')
        response = self.client.get(reverse('capsules:delete', kwargs={'pk': self.capsule.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'capsules/capsule_confirm_delete.html')

    def test_delete_capsule_action(self):
        self.client.login(username='creator', password='pass')
        response = self.client.post(reverse('capsules:delete', kwargs={'pk': self.capsule.pk}))
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(Capsule.objects.filter(pk=self.capsule.pk).exists())
