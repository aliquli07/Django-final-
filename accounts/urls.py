from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/block/', views.toggle_block_view, name='toggle_block'),
    path('users/<int:user_id>/admin/', views.toggle_admin_view, name='toggle_admin'),
]
