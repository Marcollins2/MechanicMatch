from django import forms
from .models import User, ServiceRequest
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError


class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    user_type = forms.ChoiceField(choices=[('', '---------'),('customer', 'Customer'), ('provider', 'Service Provider')], initial='')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirm_password', 'user_type']


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Ensure passwords match
        if password != confirm_password:
            raise ValidationError("Passwords do not match")

        # Optionally, validate the password using Django's built-in validation
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            raise ValidationError("Password is not valid: " + str(e))

        return cleaned_data

User = get_user_model()

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=255, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['category', 'service_provider', 'description', 'media', 'urgency_level', 'location']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'service_provider': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'media': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('low', 'Low'),
                ('medium', 'Medium'),
                ('high', 'High')
            ]),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'media': 'Upload Media (optional)',
        }


    def __init__(self, *args, **kwargs):
        super(ServiceRequestForm, self).__init__(*args, **kwargs)
        # Filter only service providers from the User model
        self.fields['service_provider'].queryset = User.objects.filter(user_type='provider')
       # Print available service providers and their IDs
        print("Available Service Providers:")
        for provider in self.fields['service_provider'].queryset:
            print(f"ID: {provider.id}, Email: {provider.email}")

    def save(self, commit=True):
        # Save the form but handle service_provider as a User instance
        instance = super(ServiceRequestForm, self).save(commit=False)
        
        # Debugging statement to check selected service provider
        selected_provider = self.cleaned_data.get('service_provider')
        print(f"Selected Service Provider: {selected_provider}")

        # Validate that the service provider exists
        if selected_provider and not User.objects.filter(id=selected_provider.id).exists():
            raise ValueError("Selected service provider does not exist")

        if commit:
            instance.save()
        return instance
    

class ServiceProviderUpdateForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['status', 'estimated_cost']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }