from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('404/', views.custom_404, name='custom_404'),

    path('projects/', views.projects_list, name='projects_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),

    path('events/', views.events_list, name='events_list'),

    # FIXED ORDER: Specific paths FIRST
    path('events/payment-success/', views.payment_success, name='payment_success'),
    path('events/<slug:slug>/create-order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),  # Must be last
]