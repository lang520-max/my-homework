from django.contrib import admin
from .models import Author, Category, Publisher, Book, User, BorrowRecord

# 注册模型到Django后台
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'publisher', 'isbn']
    list_filter = ['author', 'category', 'publisher']
    search_fields = ['title', 'isbn']
    ordering = ['title']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'id']
    search_fields = ['username', 'email']

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrow_date', 'due_date', 'return_date']
    list_filter = ['borrow_date', 'return_date']
    search_fields = ['user__username', 'book__title']
    ordering = ['-borrow_date']