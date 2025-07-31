from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    
    #Authentication
    path('login/', views.login_view, name='user_login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='user_logout'),
    
    path('change-password/', views.change_password_view, name="change_password"),
    
    #otp
    path('request-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),

]
