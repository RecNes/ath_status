"""ath URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path

from all_time_high.views import one_page_view, big_graph

urlpatterns = [
    path(f"{settings.DJANGO_ADMIN_URI}/", admin.site.urls),
    path("", one_page_view, name="main"),
    path("big_graph/<int:currency_id>", big_graph, name="big_graph")
]
