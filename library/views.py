from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User as AuthUser
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Book, Author, BorrowRecord, Category, Publisher


# 首页视图 - 重定向到仪表盘
def home(request):
    """自动跳转到仪表盘或登录页面"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('user_login')


# 登录视图
def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = AuthenticationForm()

    return render(request, 'librarys/login.html', {'form': form})


# 注册视图
def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功！欢迎使用图书馆管理系统')
            return redirect('dashboard')
        else:
            # 显示详细的表单错误
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()

    return render(request, 'librarys/register.html', {'form': form})


# 退出登录
def user_logout(request):
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('user_login')


# 仪表盘视图
@login_required
def library_dashboard(request):
    """
    图书馆管理系统仪表盘视图
    展示各种统计信息和数据
    """
    try:
        # 1. 基本统计数据
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()
        total_publishers = Publisher.objects.count()
        total_users = AuthUser.objects.count()

        # 2. 借阅相关统计
        # 当前借阅数量（未归还的）
        active_borrows = BorrowRecord.objects.filter(return_date__isnull=True).count()

        # 已归还的借阅数量
        returned_borrows = BorrowRecord.objects.filter(return_date__isnull=False).count()

        # 逾期未还的借阅数量
        overdue_borrows = BorrowRecord.objects.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now()
        ).count()

        # 3. 最新添加的图书（最近添加的5本）
        latest_books = Book.objects.select_related(
            'author', 'category', 'publisher'
        ).order_by('-id')[:5]

        # 4. 最近的借阅记录（最近5条未归还的借阅）
        recent_borrows = BorrowRecord.objects.select_related(
            'book', 'user', 'book__author'
        ).filter(
            return_date__isnull=True
        ).order_by('-borrow_date')[:5]

        # 5. 热门作者（拥有最多书籍的作者，前5名）
        popular_authors = Author.objects.annotate(
            book_count=Count('book')
        ).order_by('-book_count')[:5]

        # 6. 分类统计（每个分类的书籍数量）
        category_stats = Category.objects.annotate(
            book_count=Count('book')
        ).order_by('-book_count')

        # 7. 最近30天的借阅趋势
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_borrows_trend = BorrowRecord.objects.filter(
            borrow_date__gte=thirty_days_ago
        ).count()

        # 8. 平均借阅时长（已归还的书籍）
        returned_records = BorrowRecord.objects.filter(
            return_date__isnull=False
        )
        avg_borrow_days = 0
        if returned_records.exists():
            total_days = 0
            for record in returned_records:
                if record.borrow_date and record.return_date:
                    days = (record.return_date - record.borrow_date).days
                    total_days += days
            avg_borrow_days = round(total_days / returned_records.count(), 1)

        # 准备上下文数据
        context = {
            # 基本统计
            'total_books': total_books,
            'total_authors': total_authors,
            'total_categories': total_categories,
            'total_publishers': total_publishers,
            'total_users': total_users,

            # 借阅统计
            'active_borrows': active_borrows,
            'returned_borrows': returned_borrows,
            'overdue_borrows': overdue_borrows,
            'recent_borrows_trend': recent_borrows_trend,
            'avg_borrow_days': avg_borrow_days,

            # 数据列表
            'latest_books': latest_books,
            'recent_borrows': recent_borrows,
            'popular_authors': popular_authors,
            'category_stats': category_stats,

            # 当前时间（用于显示）
            'current_time': timezone.now(),
        }

        return render(request, 'librarys/visualization.html', context)

    except Exception as e:
        # 错误处理：如果数据库查询出错，提供默认值
        print(f"视图错误: {e}")

        context = {
            'total_books': 0,
            'total_authors': 0,
            'total_categories': 0,
            'total_publishers': 0,
            'total_users': 0,
            'active_borrows': 0,
            'returned_borrows': 0,
            'overdue_borrows': 0,
            'recent_borrows_trend': 0,
            'avg_borrow_days': 0,
            'latest_books': [],
            'recent_borrows': [],
            'popular_authors': [],
            'category_stats': [],
            'current_time': timezone.now(),
            'error_message': f"数据加载错误: {str(e)}"
        }
        return render(request, 'librarys/visualization.html', context)


# 图书列表视图
@login_required
def book_list(request):
    """图书列表视图"""
    books = Book.objects.select_related('author', 'category', 'publisher').all()
    return render(request, 'librarys/book_list.html', {'books': books})


# 作者列表视图
@login_required
def author_list(request):
    """作者列表视图"""
    authors = Author.objects.annotate(book_count=Count('book')).all()
    return render(request, 'librarys/author_list.html', {'authors': authors})


# 借阅记录视图
@login_required
def borrow_records(request):
    """借阅记录视图"""
    records = BorrowRecord.objects.select_related('book', 'user').all()
    return render(request, 'librarys/borrow_records.html', {'records': records})


# 图书管理视图
@login_required
def book_management(request):
    """图书管理页面"""
    # 获取所有图书
    books = Book.objects.select_related('author', 'category', 'publisher').all()

    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )

    # 分类筛选
    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(category__name=category_filter)

    # 获取所有分类用于筛选下拉菜单
    categories = Category.objects.all()

    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
    }
    return render(request, 'librarys/book_management.html', context)


# 添加图书视图
@login_required
def add_book(request):
    """添加新图书"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            title = request.POST.get('title')
            author_name = request.POST.get('author')
            category_name = request.POST.get('category')
            publisher_name = request.POST.get('publisher')
            isbn = request.POST.get('isbn')
            publish_date = request.POST.get('publish_date')

            # 获取或创建相关对象
            author, created = Author.objects.get_or_create(name=author_name)
            category, created = Category.objects.get_or_create(name=category_name)
            publisher, created = Publisher.objects.get_or_create(name=publisher_name)

            # 创建图书
            Book.objects.create(
                title=title,
                author=author,
                category=category,
                publisher=publisher,
                isbn=isbn,
                publish_date=publish_date
            )

            messages.success(request, f'成功添加图书《{title}》')
            return redirect('book_management')

        except Exception as e:
            messages.error(request, f'添加图书失败: {str(e)}')

    return redirect('book_management')


# 编辑图书视图
@login_required
def edit_book(request, book_id):
    """编辑图书信息"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        try:
            # 获取表单数据
            book.title = request.POST.get('title')
            author_name = request.POST.get('author')
            category_name = request.POST.get('category')
            publisher_name = request.POST.get('publisher')
            book.isbn = request.POST.get('isbn')
            book.publish_date = request.POST.get('publish_date')

            # 获取或创建相关对象
            book.author, created = Author.objects.get_or_create(name=author_name)
            book.category, created = Category.objects.get_or_create(name=category_name)
            book.publisher, created = Publisher.objects.get_or_create(name=publisher_name)

            book.save()
            messages.success(request, f'成功更新图书《{book.title}》')

        except Exception as e:
            messages.error(request, f'更新图书失败: {str(e)}')

    return redirect('book_management')


# 删除图书视图
@login_required
def delete_book(request, book_id):
    """删除图书"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        try:
            title = book.title
            book.delete()
            messages.success(request, f'成功删除图书《{title}》')
        except Exception as e:
            messages.error(request, f'删除图书失败: {str(e)}')

    return redirect('book_management')