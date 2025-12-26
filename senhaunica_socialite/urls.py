from django.urls import path
from . import views

urlpatterns = [
    path('login/usp/', views.login_init, name='senhaunica_login'),
    path('callback/', views.login_callback, name='senhaunica_callback'),
]
