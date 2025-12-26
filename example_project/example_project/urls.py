from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Library URLs
    path('', include('senhaunica_socialite.urls')),
    # Home Page
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
]
