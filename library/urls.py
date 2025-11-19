from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # 将根路径重定向到home视图
    path('', views.home, name='home'),

    # 登录注册页面
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),

    # 仪表盘（需要登录才能访问）
    path('dashboard/', views.library_dashboard, name='dashboard'),

    # 其他功能页面
    path('books/', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('borrows/', views.borrow_records, name='borrow_records'),
    path('books/manage/', views.book_management, name='book_management'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
]