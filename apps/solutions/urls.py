from django.urls import path
from . import views

urlpatterns = [
    path('', views.solutions_index, name='solutions_index'),
    path('cases/', views.cases_index, name='cases_index'),
    path('cases/<slug:slug>/', views.case_detail, name='case_detail'),
    path('<slug:slug>/', views.industry_detail, name='industry_detail'),
]
