from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_service_request, name='create_service_request'),
    path('requests/', views.service_requests_list, name='service_requests'),  
    path('provider/', views.service_provider_dashboard, name='service_provider_dashboard'),
    path('provider/update/<int:pk>/', views.update_service_request, name='update_service_request'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)