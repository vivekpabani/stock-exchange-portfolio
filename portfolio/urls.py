from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^transaction/', views.transaction, name='transaction'),
    url(r'^reset/', views.reset, name='reset'),
]
