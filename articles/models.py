from django.conf import settings
from django.db import models
from django.db.models import Avg


class Article(models.Model):
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('ai', 'AI'),
        ('cyber_security', 'Cyber Security'),
        ('cyber_sport', 'Cyber Sport'),
        ('game_development', 'Game Development'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending review'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='articles/')
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def average_rating(self):
        result = self.ratings.aggregate(avg=Avg('value'))['avg']
        return round(result, 1) if result else 0

    def ratings_count(self):
        return self.ratings.count()

    def likes_count(self):
        return self.reactions.filter(value=Reaction.LIKE).count()

    def dislikes_count(self):
        return self.reactions.filter(value=Reaction.DISLIKE).count()


class Reaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'

    VALUE_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    value = models.CharField(max_length=10, choices=VALUE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')


class Rating(models.Model):
    RATING_CHOICES = [(value, str(value)) for value in range(1, 6)]

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')


class Favorite(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='favorited_by')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'user')
