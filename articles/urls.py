from django.urls import path

from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('popular/', views.popular_list, name='popular_list'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<str:category>/', views.category_detail, name='category_detail'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<str:username>/', views.author_detail, name='author_detail'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('pending/', views.pending_list, name='pending_list'),
    path('create/', views.article_create, name='article_create'),
    path('<int:article_id>/', views.article_detail, name='article_detail'),
    path('<int:article_id>/edit/', views.article_edit, name='article_edit'),
    path('<int:article_id>/delete/', views.article_delete, name='article_delete'),
    path('<int:article_id>/approve/', views.article_approve, name='article_approve'),
    path('<int:article_id>/react/<str:value>/', views.toggle_reaction, name='toggle_reaction'),
    path('<int:article_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:article_id>/rate/', views.rate_article, name='rate_article'),
]
