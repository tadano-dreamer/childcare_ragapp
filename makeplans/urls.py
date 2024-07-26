from django.urls import path

from . import views

app_name = 'makeplans'
urlpatterns = [
    path('', views.index, name='index'),
    path('record/', views.record, name='record'),
    path('gpt/', views.gpt, name='gpt'),
    path('gpt/<str:selected_student>/<str:monthly_plan_compressed>/', views.rag, name='rag'),
]

