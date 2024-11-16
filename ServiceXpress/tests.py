from django.test import TestCase
from django.core.exceptions import ValidationError
from ServiceXpress.models import User, ServiceRequest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from ServiceXpress.models import ServiceRequest
from .forms import SignupForm, CustomLoginForm, ServiceRequestForm, ServiceProviderUpdateForm

class UserManagerTests(TestCase):

    def setUp(self):
        
        self.password = "Str0ngP@ssw0rd!"  
        self.user_data = {
            'email': 'nalunkumaberna@example.com',
            'password': self.password,
            'confirm_password': self.password,  
            'first_name': 'John',
            'last_name': 'Doe',
            'is_active': True,
            'is_staff': True
        }

    def test_create_user(self):
        
        try:
            user = User.objects.create_user(
                email=self.user_data['email'],
                password=self.user_data['password'],
                confirm_password=self.user_data['confirm_password'],
                first_name=self.user_data['first_name'],
                last_name=self.user_data['last_name'],
                is_active=self.user_data['is_active'],
                is_staff=self.user_data['is_staff']
            )
            self.assertEqual(user.email, self.user_data['email'])
            self.assertTrue(user.check_password(self.user_data['password']))
            self.assertTrue(user.is_active)
        except ValidationError as e:
            self.fail(f"User creation failed with error: {e}")

    def test_create_superuser(self):
        
        superuser_data = self.user_data.copy()
        superuser_data['is_staff'] = True
        superuser_data['is_superuser'] = True
        
        try:
            superuser = User.objects.create_superuser(
                email=superuser_data['email'],
                password=superuser_data['password'],
                confirm_password=superuser_data['confirm_password'],
                first_name=superuser_data['first_name'],
                last_name=superuser_data['last_name'],
                is_active=superuser_data['is_active'],
                is_staff=superuser_data['is_staff'],
                is_superuser=superuser_data['is_superuser']
            )
            self.assertEqual(superuser.email, superuser_data['email'])
            self.assertTrue(superuser.check_password(superuser_data['password']))
            self.assertTrue(superuser.is_staff)
            self.assertTrue(superuser.is_superuser)
        except ValidationError as e:
            self.fail(f"Superuser creation failed with error: {e}")


class ServiceRequestViewsTests(TestCase):

    def setUp(self):
        
        self.password = "Str0ngP@ssw0rd!"  
        self.customer_data = {
            'email': 'customer@example.com',
            'password': self.password,
            'confirm_password': self.password,
            'first_name': 'Customer',
            'last_name': 'One',
            'is_active': True,
            'is_staff': True,
            'user_type': 'customer'
        }
        self.provider_data = {
            'email': 'provider@example.com',
            'password': self.password,
            'confirm_password': self.password,
            'first_name': 'Provider',
            'last_name': 'One',
            'is_active': True,
            'is_staff': True,
            'user_type': 'provider'
        }

        # Create test users
        self.customer_user = User.objects.create_user(**self.customer_data)
        self.provider_user = User.objects.create_user(**self.provider_data)


    def test_create_service_request_without_login(self):
        """
        Test that a user cannot create a service request without logging in
        """
        form_data = {
            'description': 'Oil Change',
            'service_file': SimpleUploadedFile('test_file.txt', b"Test content", content_type="text/plain")
        }
        response = self.client.post(reverse('create_service_request'), data=form_data)
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("create_service_request")}')

    def test_service_provider_dashboard(self):
        """
        Test the service provider dashboard
        """
        self.client.login(username='provider@example.com', password=self.password)
        response = self.client.get(reverse('service_provider_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service_provider_dashboard.html')


    

    def test_service_requests_list(self):
        """
        Test the service requests list view
        """
        self.client.login(username='customer@example.com', password=self.password)
        service_request = ServiceRequest.objects.create(
            user=self.customer_user,
            description="Oil Change"
        )
        response = self.client.get(reverse('service_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Oil Change')


   