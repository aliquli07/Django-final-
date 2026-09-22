from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from accounts.forms import RegisterForm, LoginForm, ProfileForm
from accounts.models import Profile


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('articles:article_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('articles:article_list')
            form.add_error(None, "Username or password is incorrect, or the account is blocked")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:login')

    return render(request, 'accounts/logout_confirm.html')


@login_required
def profile_edit_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('articles:author_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def user_list_view(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can view the user list")

    User = get_user_model()
    users = User.objects.exclude(pk=request.user.pk).order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def toggle_block_view(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can block users")

    User = get_user_model()
    target = get_object_or_404(User, pk=user_id)

    if target.is_superuser:
        return HttpResponseForbidden("Super admin cannot be blocked")

    if target.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("Only super admin can block another admin")

    if request.method == 'POST':
        target.is_active = not target.is_active
        target.save()
        messages.success(
            request,
            f"{target.username} is now {'blocked' if not target.is_active else 'active'}",
        )

    return redirect('accounts:user_list')


@login_required
def toggle_admin_view(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only super admin can change admin status")

    User = get_user_model()
    target = get_object_or_404(User, pk=user_id)

    if target.is_superuser:
        return HttpResponseForbidden("Super admin status cannot be changed")

    if request.method == 'POST':
        target.is_staff = not target.is_staff
        target.save()
        messages.success(
            request,
            f"{target.username} is now {'an admin' if target.is_staff else 'a regular user'}",
        )

    return redirect('accounts:user_list')
