# library/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 首页和认证
    path('', views.home, name='home'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),

    # 管理员仪表盘 - 使用不同的路径前缀，避免与Django admin冲突
    path('library/dashboard/', views.library_dashboard, name='dashboard'),

    # 管理员功能
    path('library/books/', views.book_management, name='book_management'),
    path('library/authors/', views.author_list, name='author_list'),
    path('library/borrows/', views.borrow_records, name='borrow_records'),
    path('library/books/add/', views.add_book, name='add_book'),
    path('library/books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('library/books/<int:book_id>/delete/', views.delete_book, name='delete_book'),

    # 用户功能（借书系统）
    path('books/', views.book_list_simple, name='book_list_simple'),
    path('borrow/<int:book_id>/', views.borrow_book_simple, name='borrow_book_simple'),
    path('return/<int:record_id>/', views.return_book_simple, name='return_book_simple'),
    path('my-borrows/', views.my_borrows_simple, name='my_borrows_simple'),
    path('add-sample-data/', views.add_sample_data, name='add_sample_data'),
]