from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify/', views.otp_verify, name='verify'),
    path('joinAlem/', views.joinAlem, name='joinAlem'),
    path('login/', views.login_view, name='login'),
    path('login_verify/', views.login_verify, name='login_verify'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]
