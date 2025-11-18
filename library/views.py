# library/views.py
from django.shortcuts import render

def visualization(request):
    """处理可视化页面的视图函数"""
    return render(request, 'librarys/visualization.html')