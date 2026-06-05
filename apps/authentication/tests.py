from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class AuthenticationSecurityTests(TestCase):
    def setUp(self):
        # AllAuth is configured to authenticate by email, so we set email as the primary login field
        self.user = User.objects.create_user(
            username='testuser@organa.com',
            email='testuser@organa.com',
            password='testpassword123'
        )

    def test_homepage_redirects_unauthenticated_user_to_login(self):
        """Unauthenticated user visiting homepage should be redirected to login."""
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/accounts/login/')

    def test_dashboard_redirects_unauthenticated_user_to_login(self):
        """Unauthenticated user visiting dashboard should be redirected to login."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

    def test_dashboard_accessible_by_authenticated_user(self):
        """Authenticated user should be able to access the dashboard successfully."""
        # Use credentials parameter corresponding to AllAuth's auth method
        self.client.login(email='testuser@organa.com', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_logout_redirects_correctly(self):
        """Logging out should destroy the session and redirect back to login."""
        self.client.login(email='testuser@organa.com', password='testpassword123')
        response = self.client.post(reverse('account_logout'))
        # After logout, allauth redirects to settings.LOGOUT_REDIRECT_URL which is /accounts/login/
        self.assertRedirects(response, '/accounts/login/', fetch_redirect_response=False)
