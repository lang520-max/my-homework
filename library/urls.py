# library/urls.py
from django.urls import path
from . import views  # 从当前目录导入views模块

urlpatterns = [
    path('visualization/', views.visualization, name='visualization'),
]