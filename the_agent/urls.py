"""
URL configuration for the_agent project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter
from companies.views import (
    CompanyViewSet, chat, upload_companies_csv, chat_history,
    chat_interface, companies_interface, upload_interface, history_interface
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Web Interface Routes
    path('', chat_interface, name='home'),  # Main chat page
    path('companies/', companies_interface, name='companies'),
    path('upload/', upload_interface, name='upload'),
    path('history/', history_interface, name='history'),
    
    # API Endpoints
    path('chat/', chat, name='chat-api'),
    path('upload-csv/', upload_companies_csv, name='upload-csv'),
    path('chat-history/', chat_history, name='chat-history'),
    
    # REST API
    path("api/", include(router.urls)),
]
