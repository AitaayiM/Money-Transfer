from django.urls import path
from .views import (
    register, forgot_password, reset_password,
    login, login_verification,logout, get_all_users
)

urlpatterns = [
    path('signup/', register, name='signup'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('reset_password/<str:token>/', reset_password, name='reset_password'),
    path('login/', login, name='login'),
    path('login/verify/', login_verification, name='verify'),
    path('users/', get_all_users, name='users'),
    path('logout/', logout, name='logout'),
]
