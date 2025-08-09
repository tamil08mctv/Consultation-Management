from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),  # Ensure this exists
    path('terms/', views.terms, name='terms'),        # Ensure this exists
    path('404/', views.custom_404, name='custom_404'),
]