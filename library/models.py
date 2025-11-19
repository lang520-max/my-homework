# library/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# 删除CustomUser模型，使用Django内置User模型
# Author模型：对应AUTHOR表
class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Category模型：对应CATEGORY表
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Publisher模型：对应PUBLISHER表
class Publisher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Book模型：添加isbn字段
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    publish_date = models.DateField(null=True, blank=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return self.title


# BorrowRecord模型：使用Django内置User
class BorrowRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 使用内置User
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"