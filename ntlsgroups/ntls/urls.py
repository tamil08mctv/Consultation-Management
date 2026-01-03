from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),  # Ensure this exists
    path('terms/', views.terms, name='terms'),        # Ensure this exists
    path('404/', views.custom_404, name='custom_404'),
    # In your app's urls.py
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
]