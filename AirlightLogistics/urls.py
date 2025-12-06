"""
URL configuration for AirlightLogistics project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
# AirlightLogistics/urls.py   ← FINAL WORKING VERSION
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
import uvicorn
import threading
import os

# Simple page to show FastAPI is running separately
def start_fastapi(request):
    return HttpResponse("""
    <h1>FastAPI is running on port 8001</h1>
    <p>Open <a href="http://127.0.0.1:8001" target="_blank">http://127.0.0.1:8001</a></p>
    <p>Django is on 8000, FastAPI on 8001 → perfect combo!</p>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('fastapi/', start_fastapi),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)