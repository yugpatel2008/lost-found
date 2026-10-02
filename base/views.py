"""
Decoupled Views Module for Indus Uni. Lost & Found
Routes handlers separated by Domain & Business Logic.
"""
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from base.models import Item, UserProfile, DEPARTMENT_CHOICES
from base.utils import (
    send_credentials_email_async,
    parse_user_import_data,
    generate_sample_excel_response,
)


def _is_admin_user(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, 'profile') and user.profile.role in ['principal', 'hod', 'teacher']


# ─── Public Views ─────────────────────────────────────────────────────────────

def home(request):
    recent_items = Item.objects.all().order_by('-created_at')[:6]
    for item in recent_items:
        item.tag_list = [t.strip() for t in item.tags.split(',')] if item.tags else []
    return render(request, 'home.html', {'recent_items': recent_items})


def browse(request):
    items = Item.objects.all().order_by('-created_at')

    type_filter = request.GET.get('type', '').lower()
    if type_filter in ['lost', 'found']:
        items = items.filter(item_type=type_filter)

    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        items = items.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(tags__icontains=q) |
            Q(location_found__icontains=q)
        )

    for item in items:
        item.tag_list = [tag.strip() for tag in item.tags.split(',')] if item.tags else []

    return render(request, 'browse.html', {'items': items})


def item_detail(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
    except Item.DoesNotExist:
        messages.error(request, "Item not found.")
        return redirect('browse')

    tags = [tag.strip() for tag in item.tags.split(",")] if item.tags else []
    days_ago = (now().date() - item.date_found).days if item.date_found else None
    return render(request, 'itemdetails.html', {
        'items': item,
        'days_ago': days_ago,
        'tags': tags,
    })


@login_required(login_url='login')
def post(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type', '').strip().lower()
        if item_type not in ['lost', 'found']:
            messages.error(request, "Invalid item type. Please select 'lost' or 'found'.")
            return render(request, 'post.html')

        name           = request.POST.get('name', '').strip()
        description    = request.POST.get('description', '').strip()
        tags           = request.POST.get('tags', '').strip()
        file           = request.FILES.get('item_photo')
        date_found     = request.POST.get('date_found', '').strip()
        location_found = request.POST.get('location_found', '').strip()
        contact_info   = request.POST.get('contact_info', '').strip() or None
        meetup_place   = request.POST.get('meetup_place', '').strip() or None
        meetup_date    = request.POST.get('meetup_date', '').strip() or None
        meetup_time    = request.POST.get('meetup_time', '').strip() or None

        if not name or not description:
            messages.error(request, 'Name and description are required.')
            return render(request, 'post.html')
        if not location_found:
            messages.error(request, 'Please select a location.')
            return render(request, 'post.html')

        item = Item(
            item_type=item_type,
            name=name,
            description=description,
            tags=tags,
            file=file,
            date_found=date_found or None,
            location_found=location_found,
            contact_info=contact_info,
            meetup_place=meetup_place,
            meetup_date=meetup_date or None,
            meetup_time=meetup_time or None,
            posted_by=request.user,
        )
        item.save()

        messages.success(request, f"✓ Your {item_type} item '{name}' has been posted successfully!")
        return redirect('browse')

    return render(request, 'post.html')


def privacy(request):
    return render(request, 'privacy.html')


# ─── Auth Views ───────────────────────────────────────────────────────────────

def login(request):
    if request.user.is_authenticated:
        if _is_admin_user(request.user):
            return redirect('dashboard')
        return redirect('home')

    if request.method == 'POST':
        email_or_username = request.POST.get('email', '').strip()
        password          = request.POST.get('password', '')

        username = email_or_username
        if '@' in email_or_username:
            try:
                user_obj = User.objects.get(email__iexact=email_or_username)
                username = user_obj.username
            except User.DoesNotExist:
                username = email_or_username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)

            if _is_admin_user(user):
                return redirect('dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials. Please check your email/username and password.")

    next_param = request.GET.get('next', '')
    return render(request, 'login.html', {'next': next_param})


def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        old_password     = request.POST.get('old_password', '').strip()
        new_password     = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'change_password.html')

        if not request.user.check_password(old_password):
            messages.error(request, "Incorrect current password.")
            return render(request, 'change_password.html')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, 'change_password.html')

        if len(new_password) < 6:
            messages.error(request, "New password must be at least 6 characters long.")
            return render(request, 'change_password.html')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, "✓ Your password has been changed successfully!")
        return redirect('home')

    return render(request, 'change_password.html')


# ─── Admin Dashboard & User Management ───────────────────────────────────────

@login_required(login_url='login')
def dashboard(request):
    if not _is_admin_user(request.user):
        messages.error(request, "Access denied. Only Principal, HODs, and Teachers can access the Admin Dashboard.")
        return redirect('home')

    user_profile = getattr(request.user, 'profile', None)
    is_principal = request.user.is_superuser or (user_profile and user_profile.role == 'principal')
    user_dept    = user_profile.department if user_profile else None

    if is_principal:
        users_qs = User.objects.all().select_related('profile').order_by('-date_joined')
        items_qs = Item.objects.all().order_by('-created_at')
    else:
        users_qs = User.objects.filter(profile__department=user_dept).select_related('profile').order_by('-date_joined')
        items_qs = Item.objects.filter(location_found=user_dept).order_by('-created_at') if user_dept else Item.objects.all().order_by('-created_at')

    stats = {
        'total_users':   users_qs.count(),
        'hod_count':     User.objects.filter(profile__role='hod').count(),
        'student_count': users_qs.filter(profile__role='student').count(),
        'teacher_count': users_qs.filter(profile__role='teacher').count(),
        'total_items':   items_qs.count(),
        'found_items':   items_qs.filter(item_type='found').count(),
        'lost_items':    items_qs.filter(item_type='lost').count(),
    }

    departments = [dept[0] for dept in DEPARTMENT_CHOICES]

    return render(request, 'dashboard.html', {
        'is_principal': is_principal,
        'user_dept':    user_dept,
        'users':        users_qs,
        'items':        items_qs,
        'stats':        stats,
        'departments':  departments,
    })


@login_required(login_url='login')
def admin_create_user(request):
    if request.method != 'POST' or not _is_admin_user(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')

    user_profile = getattr(request.user, 'profile', None)
    is_principal = request.user.is_superuser or (user_profile and user_profile.role == 'principal')
    user_dept    = user_profile.department if user_profile else None

    email      = request.POST.get('email', '').strip().lower()
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    password   = request.POST.get('password', '').strip()
    role       = request.POST.get('role', 'student').strip().lower()
    department = request.POST.get('department', '').strip()

    if not email:
        messages.error(request, "Email is required.")
        return redirect('dashboard')

    if not password:
        prefix = email.split('@')[0]
        password = f"{prefix.capitalize()}@2026"

    if not is_principal:
        department = user_dept
        if role in ['principal', 'hod']:
            role = 'student'

    if role == 'student' and not email.endswith('@iite.indusuni.ac.in'):
        messages.error(request, "Student email addresses must end with '@iite.indusuni.ac.in'.")
        return redirect('dashboard')

    if User.objects.filter(email=email).exists():
        messages.error(request, f"User with email '{email}' already exists.")
        return redirect('dashboard')

    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    try:
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        new_user.profile.role = role
        new_user.profile.department = department
        new_user.profile.save()

        send_credentials_email_async(new_user, password, request)

        messages.success(request, f"✓ User '{email}' ({role.upper()}) created successfully. Credentials email sent!")
    except Exception as e:
        messages.error(request, f"Failed to create user: {e}")

    return redirect('dashboard')


@login_required(login_url='login')
def admin_bulk_create_users(request):
    if request.method != 'POST' or not _is_admin_user(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')

    user_profile = getattr(request.user, 'profile', None)
    is_principal = request.user.is_superuser or (user_profile and user_profile.role == 'principal')
    user_dept    = user_profile.department if user_profile else None

    default_role       = request.POST.get('default_role', 'student').strip().lower()
    default_department = request.POST.get('default_department', '').strip()
    excel_file         = request.FILES.get('excel_file')
    bulk_text          = request.POST.get('bulk_data', '').strip()

    if not is_principal:
        default_department = user_dept
        if default_role in ['principal', 'hod']:
            default_role = 'student'

    records = parse_user_import_data(
        uploaded_file=excel_file,
        pasted_text=bulk_text,
        default_department=default_department,
        default_role=default_role,
    )

    if not records:
        messages.error(request, "Please select an Excel/CSV file or paste user data.")
        return redirect('dashboard')

    created_count = 0
    skipped_count = 0

    for rec in records:
        email      = rec['email']
        first_name = rec['first_name']
        last_name  = rec['last_name']
        department = rec['department']
        role       = rec['role']

        if not is_principal:
            department = user_dept
            if role in ['principal', 'hod']:
                role = 'student'

        if role == 'student' and not email.endswith('@iite.indusuni.ac.in'):
            skipped_count += 1
            continue

        if User.objects.filter(email=email).exists():
            skipped_count += 1
            continue

        email_prefix = email.split('@')[0]
        generated_password = f"{email_prefix.capitalize()}@2026"

        base_username = email_prefix
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        try:
            u = User.objects.create_user(
                username=username,
                email=email,
                password=generated_password,
                first_name=first_name,
                last_name=last_name
            )
            u.profile.role = role
            u.profile.department = department
            u.profile.save()

            send_credentials_email_async(u, generated_password, request)
            created_count += 1
        except Exception:
            skipped_count += 1

    messages.success(
        request,
        f"✓ Excel Bulk Import finished: {created_count} users created successfully. ({skipped_count} skipped/duplicates/invalid domain)"
    )
    return redirect('dashboard')


@login_required(login_url='login')
def admin_delete_user(request, user_id):
    if request.method != 'POST' or not _is_admin_user(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')

    if request.user.id == user_id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('dashboard')

    user_profile = getattr(request.user, 'profile', None)
    is_principal = request.user.is_superuser or (user_profile and user_profile.role == 'principal')
    user_dept    = user_profile.department if user_profile else None

    try:
        target_user = User.objects.get(id=user_id)
        if not is_principal:
            if getattr(target_user, 'profile', None) and target_user.profile.department != user_dept:
                messages.error(request, "You can only delete users in your department.")
                return redirect('dashboard')

        username = target_user.username
        target_user.delete()
        messages.success(request, f"✓ User '{username}' deleted.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('dashboard')


@login_required(login_url='login')
def admin_delete_item(request, item_id):
    if request.method != 'POST' or not _is_admin_user(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')

    try:
        item = Item.objects.get(id=item_id)
        item_name = item.name
        item.delete()
        messages.success(request, f"✓ Item '{item_name}' removed.")
    except Item.DoesNotExist:
        messages.error(request, "Item not found.")

    return redirect('dashboard')


@login_required(login_url='login')
def admin_reset_password(request, user_id):
    if request.method != 'POST' or not _is_admin_user(request.user):
        messages.error(request, "Unauthorized action.")
        return redirect('dashboard')

    new_password = request.POST.get('new_password', '').strip()
    if not new_password:
        messages.error(request, "Password cannot be empty.")
        return redirect('dashboard')

    user_profile = getattr(request.user, 'profile', None)
    is_principal = request.user.is_superuser or (user_profile and user_profile.role == 'principal')
    user_dept    = user_profile.department if user_profile else None

    try:
        target_user = User.objects.get(id=user_id)
        if not is_principal:
            if getattr(target_user, 'profile', None) and target_user.profile.department != user_dept:
                messages.error(request, "You can only reset passwords for users in your department.")
                return redirect('dashboard')

        target_user.set_password(new_password)
        target_user.save()
        send_credentials_email_async(target_user, new_password, request)
        messages.success(request, f"✓ Password for '{target_user.email}' updated successfully and email sent.")
    except User.DoesNotExist:
        messages.error(request, "User not found.")

    return redirect('dashboard')


@login_required(login_url='login')
def download_sample_excel(request):
    return generate_sample_excel_response()


# ─── APIs ─────────────────────────────────────────────────────────────────────

def api_recent_items(request):
    items = Item.objects.all().order_by('-created_at')[:6]
    data = []
    for item in items:
        data.append({
            'id':            item.id,
            'name':          item.name,
            'description':   item.description,
            'item_type':     item.item_type,
            'location_found': item.location_found,
            'date_found':    str(item.date_found) if item.date_found else '',
            'tags':          item.tags or '',
            'file_url':      item.file.url if item.file else '',
            'meetup_place':  item.meetup_place or '',
            'meetup_date':   str(item.meetup_date) if item.meetup_date else '',
            'meetup_time':   str(item.meetup_time) if item.meetup_time else '',
        })
    return JsonResponse({'items': data})


def api_stats(request):
    return JsonResponse({
        'total_items': Item.objects.count(),
        'found_items': Item.objects.filter(item_type='found').count(),
        'lost_items':  Item.objects.filter(item_type='lost').count(),
        'total_users': User.objects.filter(is_active=True).count(),
    })
