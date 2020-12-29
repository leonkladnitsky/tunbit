"""mrAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views, appt, mortgage, life, health, coverage

urlpatterns = [
    path('content/', appt.content_view, name='content'),
    path('building/', appt.building_view, name='building'),
    path('fullprop/', appt.fullprop_view, name='fullprop'),
    path('mortgage/', mortgage.mortgage_view, name='mortgage'),
    path('life/', life.life_view, name='life'),
    path('health/', health.health_view, name='health'),
    path('coverage/', coverage.coverage_view, name='coverage'),
    path('control/', views.control_view, name='control'),
    path('', views.home_view, name='home'),
]

