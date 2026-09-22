from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from articles.forms import ArticleForm, RatingForm
from articles.models import Article, Favorite, Rating, Reaction


def _paginate(request, queryset, per_page=9):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def article_list(request):
    articles = Article.objects.filter(status='published')
    page_obj = _paginate(request, articles)
    return render(request, 'articles/article_list.html', {
        'page_obj': page_obj,
        'title': 'Articles',
    })


def popular_list(request):
    articles = (
        Article.objects.filter(status='published')
        .annotate(avg_rating=Avg('ratings__value'))
        .filter(avg_rating__gte=4)
        .order_by('-avg_rating')
    )
    page_obj = _paginate(request, articles)
    return render(request, 'articles/article_list.html', {
        'page_obj': page_obj,
        'title': 'Popular articles',
    })


def category_list(request):
    return render(request, 'articles/category_list.html', {
        'categories': Article.CATEGORY_CHOICES,
    })


def category_detail(request, category):
    category_labels = dict(Article.CATEGORY_CHOICES)
    if category not in category_labels:
        return render(request, 'articles/category_list.html', {
            'categories': Article.CATEGORY_CHOICES,
        })

    articles = Article.objects.filter(status='published', category=category)
    page_obj = _paginate(request, articles)
    return render(request, 'articles/article_list.html', {
        'page_obj': page_obj,
        'title': category_labels[category],
    })


def author_list(request):
    User = get_user_model()
    authors = (
        User.objects.filter(articles__status='published')
        .annotate(article_count=Count('articles', filter=Q(articles__status='published')))
        .distinct()
        .order_by('username')
    )
    return render(request, 'articles/author_list.html', {'authors': authors})


def author_detail(request, username):
    User = get_user_model()
    author = get_object_or_404(User, username=username)
    articles = Article.objects.filter(author=author, status='published')
    page_obj = _paginate(request, articles)
    return render(request, 'articles/author_detail.html', {
        'author': author,
        'page_obj': page_obj,
    })


@login_required
def favorites_list(request):
    articles = Article.objects.filter(favorited_by__user=request.user)
    page_obj = _paginate(request, articles)
    return render(request, 'articles/article_list.html', {
        'page_obj': page_obj,
        'title': 'Favorites',
    })


def article_detail(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if article.status != 'published':
        is_owner = request.user.is_authenticated and article.author == request.user
        is_staff = request.user.is_authenticated and request.user.is_staff
        if not is_owner and not is_staff:
            return HttpResponseForbidden("This article is not published yet")

    user_reaction = None
    is_favorite = False
    user_rating = None

    if request.user.is_authenticated:
        reaction = Reaction.objects.filter(article=article, user=request.user).first()
        user_reaction = reaction.value if reaction else None
        is_favorite = Favorite.objects.filter(article=article, user=request.user).exists()
        rating = Rating.objects.filter(article=article, user=request.user).first()
        user_rating = rating.value if rating else None

    rating_form = RatingForm(initial={'value': user_rating})

    can_manage = request.user.is_authenticated and (
        request.user == article.author or request.user.is_staff
    )

    return render(request, 'articles/article_detail.html', {
        'article': article,
        'user_reaction': user_reaction,
        'is_favorite': is_favorite,
        'rating_form': rating_form,
        'can_manage': can_manage,
    })


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'published' if request.user.is_staff else 'pending'
            article.save()
            messages.success(request, 'Article submitted')
            return redirect('articles:article_detail', article_id=article.id)
    else:
        form = ArticleForm()

    return render(request, 'articles/article_form.html', {'form': form, 'mode': 'create'})


@login_required
def article_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if article.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You can only edit your own articles")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            updated_article = form.save(commit=False)
            if not request.user.is_staff:
                updated_article.status = 'pending'
            updated_article.save()
            messages.success(request, 'Article updated')
            return redirect('articles:article_detail', article_id=article.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'articles/article_form.html', {'form': form, 'mode': 'edit', 'article': article})


@login_required
def article_delete(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if article.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You can only delete your own articles")

    if request.method == 'POST':
        article.delete()
        return redirect('articles:article_list')

    return render(request, 'articles/article_confirm_delete.html', {'article': article})


@login_required
def pending_list(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can review pending articles")

    articles = Article.objects.filter(status='pending')
    return render(request, 'articles/pending_list.html', {'articles': articles})


@login_required
def article_approve(request, article_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admins can approve articles")

    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        article.status = 'published'
        article.save()
        messages.success(request, f'"{article.title}" is now published')

    return redirect('articles:pending_list')


@login_required
def toggle_reaction(request, article_id, value):
    if request.method != 'POST' or value not in (Reaction.LIKE, Reaction.DISLIKE):
        return redirect('articles:article_detail', article_id=article_id)

    article = get_object_or_404(Article, pk=article_id)
    existing = Reaction.objects.filter(article=article, user=request.user).first()

    if existing and existing.value == value:
        existing.delete()
    elif existing:
        existing.value = value
        existing.save()
    else:
        Reaction.objects.create(article=article, user=request.user, value=value)

    return redirect('articles:article_detail', article_id=article_id)


@login_required
def toggle_favorite(request, article_id):
    if request.method != 'POST':
        return redirect('articles:article_detail', article_id=article_id)

    article = get_object_or_404(Article, pk=article_id)
    favorite = Favorite.objects.filter(article=article, user=request.user).first()

    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(article=article, user=request.user)

    return redirect('articles:article_detail', article_id=article_id)


@login_required
def rate_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                article=article,
                user=request.user,
                defaults={'value': form.cleaned_data['value']},
            )

    return redirect('articles:article_detail', article_id=article_id)
