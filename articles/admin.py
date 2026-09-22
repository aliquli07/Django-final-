from django.contrib import admin

from articles.models import Article, Favorite, Rating, Reaction


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'author', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'content', 'author__username')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'value', 'created_at')
    list_filter = ('value',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'value', 'created_at')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
