from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard$', views.dashboard, name='subscription_dashboard'),
    url(r'^explore$', views.explore, name='subscription_explore'),
]
