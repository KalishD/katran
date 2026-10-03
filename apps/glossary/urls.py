from django.urls import path
from . import views

urlpatterns = [
    path('', views.glossary_index, name='glossary_index'),
    path('<slug:slug>/', views.glossary_detail, name='glossary_detail'),
]