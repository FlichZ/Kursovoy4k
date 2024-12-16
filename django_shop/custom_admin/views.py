import zipfile
from io import BytesIO
from sqlite3 import IntegrityError

import openpyxl
from django.core.paginator import Paginator
import datetime
import os
from django.utils.timezone import now
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from django.core.management import call_command
from django.http import HttpResponse, FileResponse
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from orders.models import Order, OrderItem
from django.contrib.auth.models import User
from shop.models import Tag, Product, Review, Category, Filters
import datetime

from orders.models import Order
from django.contrib.auth.models import User
from shop.models import Tag, Product, Review


def staff_check(user):
    if not user.is_staff:
        raise PermissionDenied
    return True


# Страница с графиками для админки
from django.utils.dateparse import parse_date

@user_passes_test(staff_check)
def dashboard(request):
    # Получаем параметры для графиков
    registration_range = request.GET.get('registration_range', 'month')
    order_range = request.GET.get('order_range', 'week')

    # Обработка пользовательского диапазона
    registration_start_date = request.GET.get('registration_start_date')
    registration_end_date = request.GET.get('registration_end_date')
    order_start_date = request.GET.get('order_start_date')
    order_end_date = request.GET.get('order_end_date')

    # Преобразуем пользовательские даты в формат datetime
    reg_start = parse_date(registration_start_date) if registration_start_date else None
    reg_end = parse_date(registration_end_date) if registration_end_date else None
    ord_start = parse_date(order_start_date) if order_start_date else None
    ord_end = parse_date(order_end_date) if order_end_date else None

    # Генерируем данные для графиков
    registration_data, registration_labels = registration_activity_graph(registration_range, reg_start, reg_end)
    order_data, order_labels = order_activity_graph(order_range, ord_start, ord_end)

    # Общая статистика
    total_users = User.objects.count()
    total_sales = Order.objects.count()
    total_tags = Tag.objects.count()
    total_product = Product.objects.count()
    total_review = Review.objects.count()

    context = {
        'registration_data': registration_data,
        'registration_labels': registration_labels,
        'order_data': order_data,
        'order_labels': order_labels,
        'registration_range': registration_range,
        'order_range': order_range,
        'registration_start_date': registration_start_date,
        'registration_end_date': registration_end_date,
        'order_start_date': order_start_date,
        'order_end_date': order_end_date,
        'total_users': total_users,
        'total_review': total_review,
        'total_product': total_product,
        'total_sales': total_sales,
        'total_tags': total_tags,
    }

    return render(request, 'custom_admin/dashboard.html', context)


@user_passes_test(staff_check)
def backup_db(request):
    """Backup the database in JSON and SQL formats and create a zip file."""
    if request.method == 'POST':
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)

        # Backup in JSON format
        json_backup_path = os.path.join(backup_dir, 'backup.json')
        with open(json_backup_path, 'w') as json_file:
            call_command('dumpdata', stdout=json_file)

        # Backup in SQL format
        sql_backup_path = os.path.join(backup_dir, 'backup.sql')
        os.system(f'sqlite3 db.sqlite3 .dump > {sql_backup_path}')

        # Create a zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(json_backup_path, 'backup.json')
            zip_file.write(sql_backup_path, 'backup.sql')
        zip_buffer.seek(0)

        # Clean up temporary files
        os.remove(json_backup_path)
        os.remove(sql_backup_path)

        # Send zip file as response
        response = FileResponse(zip_buffer, as_attachment=True, filename='backup.zip')
        return response

    return HttpResponse('Invalid request method.', status=400)


@user_passes_test(staff_check)
def restore_db(request):
    """Restore the database from an uploaded JSON or SQL file."""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        backup_file = request.FILES['backup_file']
        backup_format = os.path.splitext(backup_file.name)[-1].lower()

        try:
            fs = FileSystemStorage(location='temp_backups')  # Temporary folder for backups
            os.makedirs('temp_backups', exist_ok=True)      # Ensure directory exists
            file_path = fs.save(backup_file.name, backup_file)

            if backup_format == '.json':
                # Use the file path directly with loaddata
                call_command('loaddata', os.path.join('temp_backups', file_path))
            elif backup_format == '.sql':
                # Restore from SQL
                os.system(f'sqlite3 db.sqlite3 < temp_backups/{file_path}')
            else:
                messages.error(request, 'Unsupported file format. Please upload .json or .sql files.')
                return redirect('custom_admin:dashboard')

            # Cleanup temporary backup file
            fs.delete(file_path)

            # Add success message to session
            messages.success(request, 'Database successfully restored!')
            return redirect('custom_admin:dashboard')
        except Exception as e:
            messages.error(request, f"Error restoring database: {e}")
            return redirect('custom_admin:dashboard')

    messages.error(request, 'Invalid request method or no file uploaded.')
    return redirect('custom_admin:dashboard')



# Функция для вывода графика регистрации пользователей
def registration_activity_graph(time_range, start_date=None, end_date=None):
    today = timezone.now()

    if start_date and end_date:
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%d %b')
                  for i in range((end_date - start_date).days + 1)]
        registration_data = [
            User.objects.filter(date_joined__date=start_date + datetime.timedelta(days=i)).count()
            for i in range((end_date - start_date).days + 1)
        ]
    elif time_range == 'week':
        start_date = today - datetime.timedelta(days=7)
        end_date = today
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%A') for i in range(7)]
        registration_data = [
            User.objects.filter(date_joined__date=start_date + datetime.timedelta(days=i)).count()
            for i in range(7)
        ]
    elif time_range == 'year':
        labels = [datetime.date(today.year, month, 1).strftime('%B') for month in range(1, 13)]
        registration_data = [
            User.objects.filter(
                date_joined__year=today.year,
                date_joined__month=month
            ).count()
            for month in range(1, 13)
        ]
    else:  # По умолчанию месяц
        start_date = today.replace(day=1)
        end_date = today
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%d %b')
                  for i in range((end_date - start_date).days + 1)]
        registration_data = [
            User.objects.filter(date_joined__date=start_date + datetime.timedelta(days=i)).count()
            for i in range((end_date - start_date).days + 1)
        ]

    return registration_data, labels



# Функция для вывода графика заказов по дням недели
def order_activity_graph(time_range, start_date=None, end_date=None):
    today = timezone.localtime()

    if start_date and end_date:
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%d %b')
                  for i in range((end_date - start_date).days + 1)]
        order_data = [
            Order.objects.filter(created__date=start_date + datetime.timedelta(days=i)).count()
            for i in range((end_date - start_date).days + 1)
        ]
    elif time_range == 'week':
        start_date = today - datetime.timedelta(days=7)
        end_date = today
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%A') for i in range(7)]
        order_data = [
            Order.objects.filter(created__date=start_date + datetime.timedelta(days=i)).count()
            for i in range(7)
        ]
    elif time_range == 'year':
        labels = [datetime.date(today.year, month, 1).strftime('%B') for month in range(1, 13)]
        order_data = [
            Order.objects.filter(
                created__year=today.year,
                created__month=month
            ).count()
            for month in range(1, 13)
        ]
    else:  # По умолчанию месяц
        start_date = today.replace(day=1)
        end_date = today
        labels = [(start_date + datetime.timedelta(days=i)).strftime('%d %b')
                  for i in range((end_date - start_date).days + 1)]
        order_data = [
            Order.objects.filter(created__date=start_date + datetime.timedelta(days=i)).count()
            for i in range((end_date - start_date).days + 1)
        ]

    return order_data, labels


@user_passes_test(staff_check)
def generate_report(request):
    """Generate an Excel report of purchased products."""
    # Create a workbook and a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Отчет о покупках"

    # Add headers
    headers = ["ID товара", "Название", "Количество", "Общая стоимость", "Дата покупки"]
    worksheet.append(headers)

    # Fetch data
    order_items = OrderItem.objects.select_related("product", "order").all()

    # Add data to the worksheet
    for item in order_items:
        worksheet.append([
            item.product.id,
            item.product.title,
            item.quantity,
            item.price * item.quantity,
            item.order.created.strftime("%Y-%m-%d"),
        ])

    # Auto-adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter  # Get the column name
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        worksheet.column_dimensions[column_letter].width = max_length + 2

    # Generate a filename
    report_filename = f"Отчет_о_покупках_{now().strftime('%Y-%m-%d')}.xlsx"

    # Create an HTTP response with Excel content
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{report_filename}"'

    # Save the workbook to the response
    workbook.save(response)
    return response


@user_passes_test(staff_check)
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username or not email or not password:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/user_form.html')

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            messages.success(request, 'Пользователь успешно создан')
            return redirect('custom_admin:user_list')
        except Exception as e:
            messages.error(request, f'Ошибка при создании пользователя: {e}')
            return render(request, 'custom_admin/crud/user_form.html')

    return render(request, 'custom_admin/crud/user_form.html')


@user_passes_test(staff_check)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        if not username or not email:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/user_form.html', {'user': user})

        try:
            user.username = username
            user.email = email
            user.save()
            messages.success(request, 'Данные пользователя успешно обновлены')
            return redirect('custom_admin:user_list')
        except Exception as e:
            messages.error(request, f'Ошибка при обновлении пользователя: {e}')
            return render(request, 'custom_admin/crud/user_form.html', {'user': user})

    return render(request, 'custom_admin/crud/user_form.html', {'user': user})


@user_passes_test(staff_check)
def user_list(request):
    query = request.GET.get('q', '')  # Получаем параметр поиска из GET-запроса
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    )  # Фильтруем пользователей по логину или email
    paginator = Paginator(users, 10)  # Количество пользователей на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'custom_admin/CRUD/user_list.html', {'page_obj': page_obj, 'query': query})


@user_passes_test(staff_check)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        user.delete()
        messages.success(request, 'Пользователь успешно удален')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении пользователя: {e}')
    return redirect('custom_admin:user_list')


# CRUD: Продукты
@user_passes_test(staff_check)
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    category_filter = request.GET.get('category')

    if category_filter:
        products = products.filter(category__id=category_filter)

    if not products.exists():
        messages.info(request, 'Нет продуктов в базе данных.')

    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paginated_products = paginator.get_page(page)

    return render(request, 'custom_admin/crud/product_list.html', {
        'products': paginated_products,
        'categories': categories,
        'category_filter': category_filter
    })

    if not paginated_products: messages.info(request, 'Нет продуктов в базе данных.')

@user_passes_test(staff_check)
def product_create(request):
    categories = Category.objects.all()
    tags = Tag.objects.all()  # Получаем все теги
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        selected_tags = request.POST.getlist('tags')  # Получаем выбранные теги

        if not title or not slug or not price or not description or not category:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/product_form.html', {'categories': categories, 'tags': tags})

        try:
            product = Product.objects.create(
                title=title,
                slug=slug,
                price=price,
                description=description,
                category_id=category
            )
            product.tags.set(selected_tags)  # Устанавливаем теги для продукта
            messages.success(request, 'Продукт успешно создан')
            return redirect('custom_admin:product_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при сохранении продукта в базе данных.')
            return render(request, 'custom_admin/crud/product_form.html', {'categories': categories, 'tags': tags})

    return render(request, 'custom_admin/crud/product_form.html', {'categories': categories, 'tags': tags})


@user_passes_test(staff_check)
def product_edit(request, pk):
    product = Product.objects.get(id=pk)
    categories = Category.objects.all()
    tags = Tag.objects.all()  # Получаем все теги
    if request.method == 'POST':
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        selected_tags = request.POST.getlist('tags')  # Получаем выбранные теги

        if not title or not slug or not price or not description or not category:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/product_form.html', {
                'categories': categories,
                'tags': tags,
                'product': product
            })

        try:
            product.title = title
            product.slug = slug
            product.price = price
            product.description = description
            product.category_id = category
            product.save()
            product.tags.set(selected_tags)  # Обновляем теги продукта
            messages.success(request, 'Продукт обновлен успешно')
            return redirect('custom_admin:product_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при обновлении продукта.')
            return render(request, 'custom_admin/crud/product_form.html', {
                'categories': categories,
                'tags': tags,
                'product': product
            })

    return render(request, 'custom_admin/crud/product_form.html', {
        'categories': categories,
        'tags': tags,
        'product': product
    })

@user_passes_test(staff_check)
def product_delete(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    messages.success(request, 'Продукт удален успешно')
    return redirect('custom_admin:product_list')

# CRUD: Фильтры
@user_passes_test(staff_check)
def filter_list(request):
    filters = Filters.objects.all()
    paginator = Paginator(filters, 10)
    page = request.GET.get('page')
    paginated_filters = paginator.get_page(page)

    if not paginated_filters:
        messages.info(request, 'Нет фильтров в базе данных.')

    return render(request, 'custom_admin/crud/filter_list.html', {'filters': paginated_filters})


@user_passes_test(staff_check)
def filter_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        if not name or not slug:
            messages.error(request, 'Имя и слаг фильтра обязательны для заполнения.')
            return render(request, 'custom_admin/crud/filter_form.html')

        try:
            filter_obj = Filters.objects.create(name=name, slug=slug)
            messages.success(request, 'Фильтр успешно создан')
            return redirect('custom_admin:filter_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при сохранении фильтра в базе данных.')

    return render(request, 'custom_admin/crud/filter_form.html')


@user_passes_test(staff_check)
def filter_edit(request, pk):
    filter_obj = Filters.objects.get(id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        if not name or not slug:
            messages.error(request, 'Имя и слаг фильтра обязательны для заполнения.')
            return render(request, 'custom_admin/crud/filter_form.html', {'filter': filter_obj})

        try:
            filter_obj.name = name
            filter_obj.slug = slug
            filter_obj.save()
            messages.success(request, 'Фильтр обновлен успешно')
            return redirect('custom_admin:filter_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при обновлении фильтра.')

    return render(request, 'custom_admin/crud/filter_form.html', {'filter': filter_obj})


@user_passes_test(staff_check)
def filter_delete(request, pk):
    filter_obj = Filters.objects.get(id=pk)
    filter_obj.delete()
    messages.success(request, 'Фильтр удален успешно')
    return redirect('custom_admin:filter_list')


# CRUD: Теги
@user_passes_test(staff_check)
def tag_list(request):
    tags = Tag.objects.all()
    paginator = Paginator(tags, 10)
    page = request.GET.get('page')
    paginated_tags = paginator.get_page(page)

    if not paginated_tags:
        messages.info(request, 'Нет тегов в базе данных.')

    return render(request, 'custom_admin/crud/tag_list.html', {'tags': paginated_tags})



@user_passes_test(staff_check)
def tag_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'Имя тега обязательно для заполнения.')
            return render(request, 'custom_admin/crud/tag_form.html')

        try:
            tag = Tag.objects.create(name=name)
            messages.success(request, 'Тег успешно создан')
            return redirect('custom_admin:tag_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при сохранении тега в базе данных.')

    return render(request, 'custom_admin/crud/tag_form.html')


@user_passes_test(staff_check)
def tag_edit(request, pk):
    tag = Tag.objects.get(id=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'Имя тега обязательно для заполнения.')
            return render(request, 'custom_admin/crud/tag_form.html', {'tag': tag})

        try:
            tag.name = name
            tag.save()
            messages.success(request, 'Тег обновлен успешно')
            return redirect('custom_admin:tag_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при обновлении тега.')

    return render(request, 'custom_admin/crud/tag_form.html', {'tag': tag})


@user_passes_test(staff_check)
def tag_delete(request, pk):
    tag = Tag.objects.get(id=pk)
    tag.delete()
    messages.success(request, 'Тег удален успешно')
    return redirect('custom_admin:tag_list')


# CRUD: Отзывы
@user_passes_test(staff_check)
def review_list(request):
    reviews = Review.objects.all()
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    paginated_reviews = paginator.get_page(page)

    if not paginated_reviews:
        messages.info(request, 'Нет отзывов в базе данных.')

    return render(request, 'custom_admin/crud/review_list.html', {'reviews': paginated_reviews})



@user_passes_test(staff_check)
def review_create(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        product = request.POST.get('product')
        if not content or not product:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/review_form.html')

        try:
            review = Review.objects.create(content=content, product_id=product)
            messages.success(request, 'Отзыв успешно добавлен')
            return redirect('custom_admin:review_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при добавлении отзыва.')

    products = Product.objects.all()
    return render(request, 'custom_admin/crud/review_form.html', {'products': products})


@user_passes_test(staff_check)
def review_edit(request, pk):
    review = Review.objects.get(id=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        product = request.POST.get('product')
        if not content or not product:
            messages.error(request, 'Все поля должны быть заполнены.')
            return render(request, 'custom_admin/crud/review_form.html', {'review': review})

        try:
            review.content = content
            review.product_id = product
            review.save()
            messages.success(request, 'Отзыв обновлен успешно')
            return redirect('custom_admin:review_list')
        except IntegrityError:
            messages.error(request, 'Ошибка при обновлении отзыва.')

    products = Product.objects.all()
    return render(request, 'custom_admin/crud/review_form.html', {'review': review, 'products': products})


@user_passes_test(staff_check)
def review_delete(request, pk):
    review = Review.objects.get(id=pk)
    review.delete()
    messages.success(request, 'Отзыв удален успешно')
    return redirect('custom_admin:review_list')


@user_passes_test(staff_check)
def category_list(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 10)
    page = request.GET.get('page')
    paginated_categories = paginator.get_page(page)

    if not paginated_categories:
        messages.info(request, 'Нет категорий в базе данных.')

    return render(request, 'custom_admin/crud/category_list.html', {'categories': paginated_categories})


@user_passes_test(staff_check)
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        Category.objects.create(name=name, slug=slug)
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/crud/category_form.html')

@user_passes_test(staff_check)
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/crud/category_form.html', {'category': category})

@user_passes_test(staff_check)
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('custom_admin:category_list')

# CRUD заказов
@user_passes_test(staff_check)
def order_list(request):
    query = request.GET.get('search', '')  # Получаем значение поискового запроса
    orders = Order.objects.all()

    # Если есть поисковый запрос, фильтруем по ключевым полям
    if query:
        orders = orders.filter(
            first_name__icontains=query
        ) | orders.filter(
            last_name__icontains=query
        ) | orders.filter(
            email__icontains=query
        ) | orders.filter(
            city__icontains=query
        )

    paginator = Paginator(orders, 10)  # Показываем 10 заказов на странице
    page = request.GET.get('page')
    paginated_orders = paginator.get_page(page)

    if not orders.exists():
        messages.info(request, 'По вашему запросу ничего не найдено.')

    return render(request, 'custom_admin/crud/order_list.html', {
        'orders': paginated_orders,
        'search_query': query,  # Передаем текущий поисковый запрос в шаблон
    })



@user_passes_test(staff_check)
def order_edit(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order.first_name = request.POST.get('first_name')
        order.last_name = request.POST.get('last_name')
        order.email = request.POST.get('email')
        order.address = request.POST.get('address')
        order.postal_code = request.POST.get('postal_code')
        order.city = request.POST.get('city')
        order.paid = bool(request.POST.get('paid'))
        order.save()
        return redirect('custom_admin:order_list')
    return render(request, 'custom_admin/crud/order_form.html', {'order': order})

@user_passes_test(staff_check)
def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('custom_admin:order_list')

#  заказанных товаров
@user_passes_test(staff_check)
def orderitem_list(request):
    order_items = OrderItem.objects.all()
    paginator = Paginator(order_items, 10)
    page = request.GET.get('page')
    paginated_order_items = paginator.get_page(page)

    if not paginated_order_items:
        messages.info(request, 'Нет товаров в заказах.')

    return render(request, 'custom_admin/crud/orderitem_list.html', {'order_items': paginated_order_items})


@user_passes_test(staff_check)
def orderitem_edit(request, id):
    order_item = get_object_or_404(OrderItem, id=id)
    if request.method == 'POST':
        order_item.price = request.POST.get('price')
        order_item.quantity = request.POST.get('quantity')
        order_item.save()
        return redirect('custom_admin:orderitem_list')
    return render(request, 'custom_admin/crud/orderitem_form.html', {'order_item': order_item})

@user_passes_test(staff_check)
def orderitem_delete(request, id):
    order_item = get_object_or_404(OrderItem, id=id)
    order_item.delete()
    return redirect('custom_admin:orderitem_list')