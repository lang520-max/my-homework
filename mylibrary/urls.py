from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls')),  # 包含library应用的URL
    path('', RedirectView.as_view(url='/visualization/')),
]