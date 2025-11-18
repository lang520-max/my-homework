# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 主页和仪表盘
    path('', views.library_dashboard, name='dashboard'),
    # 列表页面
    path('books/', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('borrows/', views.borrow_records, name='borrow_records'),
    # 图书管理功能
    path('books/manage/', views.book_management, name='book_management'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
]