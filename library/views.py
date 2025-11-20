from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Book, BorrowRecord, Author, Category, Publisher


def home(request):
    """首页 - 根据认证状态重定向"""
    if request.user.is_authenticated:
        if request.user.is_staff:  # 管理员进入仪表盘
            return redirect('dashboard')
        else:  # 普通用户进入图书列表
            return redirect('book_list_simple')
    else:  # 未登录用户进入登录页面
        return redirect('user_login')


def user_login(request):
    """用户登录"""
    # 如果用户已登录，直接重定向到相应页面
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('book_list_simple')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # 根据用户类型重定向到不同页面
                if user.is_staff:
                    messages.success(request, f'欢迎回来，管理员 {user.username}')
                    return redirect('dashboard')
                else:
                    messages.success(request, f'欢迎回来，{user.username}')
                    return redirect('book_list_simple')
            else:
                messages.error(request, '用户名或密码错误')
        else:
            messages.error(request, '用户名或密码错误')
    else:
        form = AuthenticationForm()

    return render(request, 'librarys/login.html', {'form': form})


def user_register(request):
    """用户注册"""
    # 如果用户已登录，直接重定向
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('book_list_simple')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 新注册用户默认为普通用户
            user.is_staff = False
            user.save()

            # 自动登录
            login(request, user)
            messages.success(request, '注册成功！欢迎使用图书馆管理系统')
            return redirect('book_list_simple')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = UserCreationForm()

    return render(request, 'librarys/register.html', {'form': form})


def user_logout(request):
    """用户退出登录"""
    logout(request)
    messages.info(request, '您已成功退出登录')
    return redirect('user_login')


@login_required
def book_list_simple(request):
    """简化版图书列表 - 普通用户界面"""
    books = Book.objects.all().select_related('author', 'category', 'publisher')

    # 标记每本书的借阅状态
    for book in books:
        book.is_borrowed = BorrowRecord.objects.filter(
            user=request.user,
            book=book,
            return_date__isnull=True
        ).exists()

    # 获取当前用户的借阅统计
    current_borrows = BorrowRecord.objects.filter(
        user=request.user,
        return_date__isnull=True
    )
    borrow_history = BorrowRecord.objects.filter(
        user=request.user,
        return_date__isnull=False
    ).order_by('-return_date')[:5]

    # 计算逾期状态
    for record in current_borrows:
        record.is_overdue = timezone.now() > record.due_date
        if record.is_overdue:
            record.overdue_days = (timezone.now().date() - record.due_date.date()).days

    context = {
        'books': books,
        'current_user': request.user,
        'current_borrows': current_borrows,
        'borrow_history': borrow_history,
        'current_count': current_borrows.count(),
        'total_count': BorrowRecord.objects.filter(user=request.user).count(),
    }

    return render(request, 'librarys/book_list_simple.html', context)


@login_required
def borrow_book_simple(request, book_id):
    """借书功能"""
    book = get_object_or_404(Book, id=book_id)

    # 检查是否已经借阅此书且未归还
    existing_borrow = BorrowRecord.objects.filter(
        user=request.user,
        book=book,
        return_date__isnull=True
    ).exists()

    if existing_borrow:
        messages.error(request, f'您已经借阅了《{book.title}》，请先归还')
        return redirect('my_borrows_simple')

    # 计算应还日期（借期30天）
    due_date = timezone.now() + timedelta(days=30)

    # 创建借阅记录
    BorrowRecord.objects.create(
        user=request.user,
        book=book,
        borrow_date=timezone.now(),
        due_date=due_date
    )

    messages.success(request, f'成功借阅《{book.title}》！应还日期：{due_date.strftime("%Y-%m-%d")}')
    return redirect('book_list_simple')


@login_required
def return_book_simple(request, record_id):
    """还书功能"""
    borrow_record = get_object_or_404(BorrowRecord, id=record_id)

    # 检查权限：用户只能归还自己的书
    if borrow_record.user != request.user:
        messages.error(request, '您没有权限归还此书')
        return redirect('book_list_simple')

    # 检查是否已归还
    if borrow_record.return_date:
        messages.error(request, '这本书已经归还过了')
        return redirect('my_borrows_simple')

    # 执行还书
    borrow_record.return_date = timezone.now()
    borrow_record.save()

    # 检查是否逾期
    if timezone.now() > borrow_record.due_date:
        overdue_days = (timezone.now().date() - borrow_record.due_date.date()).days
        messages.warning(request, f'归还成功！本书逾期 {overdue_days} 天')
    else:
        messages.success(request, f'成功归还《{borrow_record.book.title}》')

    return redirect('my_borrows_simple')


@login_required
def my_borrows_simple(request):
    """我的借阅页面"""
    # 当前借阅（未归还）
    current_borrows = BorrowRecord.objects.filter(
        user=request.user,
        return_date__isnull=True
    ).select_related('book', 'book__author')

    # 计算逾期状态
    for record in current_borrows:
        record.is_overdue = timezone.now() > record.due_date
        if record.is_overdue:
            record.overdue_days = (timezone.now().date() - record.due_date.date()).days

    # 借阅历史（已归还，最近5条）
    borrow_history = BorrowRecord.objects.filter(
        user=request.user,
        return_date__isnull=False
    ).select_related('book', 'book__author').order_by('-return_date')[:5]

    # 统计信息
    current_count = current_borrows.count()
    total_count = BorrowRecord.objects.filter(user=request.user).count()

    return render(request, 'librarys/my_borrows_simple.html', {
        'current_borrows': current_borrows,
        'borrow_history': borrow_history,
        'current_user': request.user,
        'current_count': current_count,
        'total_count': total_count
    })


def add_sample_data(request):
    """添加示例数据（用于测试）"""
    # 添加示例作者
    author1, created = Author.objects.get_or_create(name="刘慈欣")
    author2, created = Author.objects.get_or_create(name="J.K.罗琳")
    author3, created = Author.objects.get_or_create(name="余华")

    # 添加示例分类
    category1, created = Category.objects.get_or_create(name="科幻")
    category2, created = Category.objects.get_or_create(name="奇幻")
    category3, created = Category.objects.get_or_create(name="文学")

    # 添加示例出版社
    publisher1, created = Publisher.objects.get_or_create(name="重庆出版社")
    publisher2, created = Publisher.objects.get_or_create(name="人民文学出版社")
    publisher3, created = Publisher.objects.get_or_create(name="作家出版社")

    # 添加示例图书
    books_data = [
        {"title": "三体", "author": author1, "category": category1, "publisher": publisher1, "isbn": "9787229030933"},
        {"title": "哈利波特与魔法石", "author": author2, "category": category2, "publisher": publisher2,
         "isbn": "9787020033430"},
        {"title": "活着", "author": author3, "category": category3, "publisher": publisher3, "isbn": "9787506365437"},
        {"title": "流浪地球", "author": author1, "category": category1, "publisher": publisher1,
         "isbn": "9787229112752"},
        {"title": "球状闪电", "author": author1, "category": category1, "publisher": publisher1,
         "isbn": "9787229102753"},
    ]

    for book_data in books_data:
        Book.objects.get_or_create(
            title=book_data["title"],
            defaults={
                'author': book_data["author"],
                'category': book_data["category"],
                'publisher': book_data["publisher"],
                'isbn': book_data["isbn"],
                'publish_date': timezone.now().date()
            }
        )

    messages.success(request, '示例数据添加成功！')
    return redirect('book_list_simple')


@login_required
def dashboard(request):
    """图书馆管理系统仪表盘视图 - 管理员界面"""
    # 检查是否为管理员
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问管理员界面')
        return redirect('book_list_simple')

    try:
        # 1. 基本统计数据
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()
        total_publishers = Publisher.objects.count()
        total_users = User.objects.count()

        # 2. 借阅相关统计
        active_borrows = BorrowRecord.objects.filter(return_date__isnull=True).count()
        returned_borrows = BorrowRecord.objects.filter(return_date__isnull=False).count()
        overdue_borrows = BorrowRecord.objects.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now()
        ).count()

        # 3. 最新添加的图书
        latest_books = Book.objects.select_related('author', 'category', 'publisher').order_by('-id')[:5]

        # 4. 最近的借阅记录
        recent_borrows = BorrowRecord.objects.select_related('book', 'user', 'book__author').filter(
            return_date__isnull=True
        ).order_by('-borrow_date')[:5]

        # 5. 热门作者
        popular_authors = Author.objects.annotate(book_count=Count('book')).order_by('-book_count')[:5]

        # 6. 分类统计
        category_stats = Category.objects.annotate(book_count=Count('book')).order_by('-book_count')

        # 7. 最近30天的借阅趋势
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_borrows_trend = BorrowRecord.objects.filter(borrow_date__gte=thirty_days_ago).count()

        # 8. 平均借阅时长
        returned_records = BorrowRecord.objects.filter(return_date__isnull=False)
        avg_borrow_days = 0
        if returned_records.exists():
            total_days = 0
            for record in returned_records:
                if record.borrow_date and record.return_date:
                    days = (record.return_date - record.borrow_date).days
                    total_days += days
            avg_borrow_days = round(total_days / returned_records.count(), 1)

        context = {
            'total_books': total_books,
            'total_authors': total_authors,
            'total_categories': total_categories,
            'total_publishers': total_publishers,
            'total_users': total_users,
            'active_borrows': active_borrows,
            'returned_borrows': returned_borrows,
            'overdue_borrows': overdue_borrows,
            'recent_borrows_trend': recent_borrows_trend,
            'avg_borrow_days': avg_borrow_days,
            'latest_books': latest_books,
            'recent_borrows': recent_borrows,
            'popular_authors': popular_authors,
            'category_stats': category_stats,
            'current_time': timezone.now(),
        }

        return render(request, 'librarys/visualization.html', context)

    except Exception as e:
        print(f"仪表盘视图错误: {e}")
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


# 以下为管理员功能页面（需要管理员权限）
@login_required
def book_management(request):
    """图书管理页面 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('book_list_simple')

    books = Book.objects.select_related('author', 'category', 'publisher').all()
    search_query = request.GET.get('search', '')

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__name__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )

    category_filter = request.GET.get('category', '')
    if category_filter:
        books = books.filter(category__name=category_filter)

    categories = Category.objects.all()

    context = {
        'books': books,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
    }
    return render(request, 'librarys/book_management.html', context)


@login_required
def author_list(request):
    """作者列表视图 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('book_list_simple')

    authors = Author.objects.annotate(book_count=Count('book')).all()
    return render(request, 'librarys/author_list.html', {'authors': authors})


@login_required
def borrow_records(request):
    """借阅记录视图 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限访问此页面')
        return redirect('book_list_simple')

    records = BorrowRecord.objects.select_related('book', 'user').all()
    return render(request, 'librarys/borrow_records.html', {'records': records})


@login_required
def add_book(request):
    """添加新图书 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限执行此操作')
        return redirect('book_list_simple')

    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            author_name = request.POST.get('author')
            category_name = request.POST.get('category')
            publisher_name = request.POST.get('publisher')
            isbn = request.POST.get('isbn')
            publish_date = request.POST.get('publish_date')

            author, created = Author.objects.get_or_create(name=author_name)
            category, created = Category.objects.get_or_create(name=category_name)
            publisher, created = Publisher.objects.get_or_create(name=publisher_name)

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


@login_required
def edit_book(request, book_id):
    """编辑图书信息 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限执行此操作')
        return redirect('book_list_simple')

    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        try:
            book.title = request.POST.get('title')
            author_name = request.POST.get('author')
            category_name = request.POST.get('category')
            publisher_name = request.POST.get('publisher')
            book.isbn = request.POST.get('isbn')
            book.publish_date = request.POST.get('publish_date')

            book.author, created = Author.objects.get_or_create(name=author_name)
            book.category, created = Category.objects.get_or_create(name=category_name)
            book.publisher, created = Publisher.objects.get_or_create(name=publisher_name)

            book.save()
            messages.success(request, f'成功更新图书《{book.title}》')

        except Exception as e:
            messages.error(request, f'更新图书失败: {str(e)}')

    return redirect('book_management')


@login_required
def delete_book(request, book_id):
    """删除图书 - 管理员功能"""
    if not request.user.is_staff:
        messages.error(request, '您没有权限执行此操作')
        return redirect('book_list_simple')

    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        try:
            title = book.title
            book.delete()
            messages.success(request, f'成功删除图书《{title}》')
        except Exception as e:
            messages.error(request, f'删除图书失败: {str(e)}')

    return redirect('book_management')