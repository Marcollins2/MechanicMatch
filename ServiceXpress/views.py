from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import User, ServiceRequest
from django.contrib import messages
from .forms import CustomLoginForm, SignupForm, ServiceRequestForm, ServiceProviderUpdateForm
from django.contrib.auth.decorators import login_required
from django.utils.html import escape


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['user_type']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            # Ensure the passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'signup.html', {'form': form})

            # Create the user instance
            user = form.save(commit=False)
            user.set_password(password)

            # Set user type fields
            if user_type == 'customer':
                user.is_customer = True
                user.is_active = True
                user.is_staff = False
            elif user_type == 'provider':
                user.is_service_provider = True
                user.is_active = True
                user.is_staff = True

            # Save the user and log them in
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('login')  # Or to a different page like 'home'

        else:
            # If form is not valid, return with error messages
            messages.error(request, "There were some errors in the form. Please check and try again.")

    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                request.session.flush()
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name}!')

                # Redirect based on user type
                if user.user_type == 'customer':
                    return redirect('create_service_request')  # e.g., Customer dashboard
                elif user.user_type == 'provider':
                    return redirect('service_provider_dashboard')  # e.g., Service Provider dashboard
                
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Error validating the form')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    request.session.flush()
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# View to create a new service request
@login_required
def create_service_request(request):
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.description = escape(form.cleaned_data['description'])
            service_request.save()
            messages.success(request, 'Service request submitted successfully!')
            return redirect('service_requests')
    else:
        form = ServiceRequestForm()
    return render(request, 'create_service_request.html', {'form': form})

# View to list all service requests made by the logged-in user
@login_required
def service_requests_list(request):
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-time')
    return render(request, 'service_requests_list.html', {'requests': requests})


# View for service providers to see and update requests
@login_required
def service_provider_dashboard(request):

    
    requests = ServiceRequest.objects.filter(service_provider=request.user)
    return render(request, 'service_provider_dashboard.html', {'requests': requests})

@login_required
def update_service_request(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    if request.method == 'POST':
        form = ServiceProviderUpdateForm(request.POST, instance=service_request)
        if form.is_valid():
            updated_request = form.save(commit=False)
            updated_request.service_provider = request.user
            updated_request.save()
            messages.success(request, 'Service request updated successfully!')
            return redirect('service_provider_dashboard')
    else:
        form = ServiceProviderUpdateForm(instance=service_request)
    return render(request, 'update_service_request.html', {'form': form, 'service_request': service_request})