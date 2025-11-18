from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls')),  # 包含library应用的URL
    path('', RedirectView.as_view(url='/visualization/')), # 添加重定向，将根路径重定向到可视化页面
]