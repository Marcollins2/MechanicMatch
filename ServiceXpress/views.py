from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import User, ServiceRequest
from django.contrib import messages
from .forms import CustomLoginForm, SignupForm, ServiceRequestForm, ServiceProviderUpdateForm
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
import plotly.graph_objs as go
from plotly.offline import plot
from django.db.models import Count

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
                request.session.flush() # Clears out old session data
                login(request, user) # Logs in the user with a new session ID
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
    request.session.flush()  # Clears out old session data
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
def generate_plotly_charts(request):
    # Filter data by the current user
    category_data = ServiceRequest.objects.filter(user=request.user).values('category').annotate(count=Count('category'))
    status_data = ServiceRequest.objects.filter(user=request.user).values('status').annotate(count=Count('status'))
    
    # Extract data for the pie chart (categories)
    categories = [item['category'] for item in category_data]
    category_counts = [item['count'] for item in category_data]

    # Extract data for the bar chart (statuses)
    statuses = [item['status'] for item in status_data]
    status_counts = [item['count'] for item in status_data]

    # Plotly Pie Chart for Categories
    pie_chart = go.Figure(data=[go.Pie(labels=categories, values=category_counts, hole=0.3)])
    pie_chart.update_layout(title='Service Request Categories')

    # Convert the pie chart to HTML
    pie_div = plot(pie_chart, output_type='div', include_plotlyjs=False)

    # Plotly Bar Chart for Statuses
    bar_chart = go.Figure(data=[go.Bar(x=statuses, y=status_counts, marker_color='skyblue')])
    bar_chart.update_layout(
        title='Service Request Statuses',
        xaxis_title='Status',
        yaxis_title='Count'
    )

    # Convert the bar chart to HTML
    bar_div = plot(bar_chart, output_type='div', include_plotlyjs=False)

    return pie_div, bar_div

# New view for rendering the charts page
def charts_page(request):
    # Generate Plotly charts
    pie_chart, bar_chart = generate_plotly_charts(request)
    
    return render(request, 'charts.html', {
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
    })

def service_requests_list(request):
    # Fetch service requests for the current user
    requests = ServiceRequest.objects.filter(user=request.user).order_by('-time')
    return render(request, 'service_requests_list.html', {
        'requests': requests,
    })

# View for service providers to see and update requests
@login_required
def service_provider_dashboard(request):

    
    requests = ServiceRequest.objects.filter(service_provider=request.user)
    return render(request, 'service_provider_dashboard.html', {'requests': requests})

@login_required
def update_service_request(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    if request.user != service_request.user and not request.user.is_service_provider:
        return HttpResponseForbidden()

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

def generate_charts():
    # Query the database for category and status counts
    category_data = ServiceRequest.objects.values('category').annotate(count=Count('category'))
    status_data = ServiceRequest.objects.values('status').annotate(count=Count('status'))
    
    # Extract data for the pie chart (categories)
    categories = [item['category'] for item in category_data]
    category_counts = [item['count'] for item in category_data]

    # Extract data for the bar chart (statuses)
    statuses = [item['status'] for item in status_data]
    status_counts = [item['count'] for item in status_data]

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Plot Pie Chart for Categories
    ax1.pie(category_counts, labels=categories, autopct='%1.1f%%', startangle=90, colors=['#66c2a5', '#fc8d62', '#8da0cb'])
    ax1.set_title('Service Request Categories')

    # Plot Bar Chart for Statuses
    ax2.bar(statuses, status_counts, color=['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3'])
    ax2.set_title('Service Request Statuses')
    ax2.set_xlabel('Status')
    ax2.set_ylabel('Count')
    
    # Adjust layout
    plt.tight_layout()

    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Encode the image to display in HTML
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    
    return image_base64

def service_charts_view(request):
    chart_image = generate_charts()
    return render(request, 'service_charts.html', {'chart_image': chart_image})