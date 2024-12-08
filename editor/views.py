from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Review
from journalist.models import Article,Category
from users.decorators import role_required
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q


@role_required('editor')
def editor_dashboard(request):
    # Get the search query and category filter from request
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    # Filter the articles based on search and category
    articles = Article.objects.all()
    categories = Category.objects.all()

    if search_query:
        articles = articles.filter(Q(title__icontains=search_query))
    
    if category_filter:
        articles = articles.filter(category__name=category_filter)  # Assuming category is a ForeignKey to a Category model

    # Separate the submitted and reviewed articles
    submitted_articles = articles.filter(status='submitted')
    reviewed_articles = articles.exclude(status='submitted')

    # Pagination
    paginator = Paginator(submitted_articles, 3)  
    page = request.GET.get('page')
    paginated_submitted_articles = paginator.get_page(page)

    paginator_reviewed = Paginator(reviewed_articles, 3)
    page_reviewed = request.GET.get('page_reviewed')
    paginated_reviewed_articles = paginator_reviewed.get_page(page_reviewed)

    return render(request, 'editor_dashboard.html', {
        'submitted_articles': paginated_submitted_articles,
        'reviewed_articles': paginated_reviewed_articles,
        'search_query': search_query,
        'categories': categories,
        'category_filter': category_filter,
    })

@role_required('editor')
def review_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    journalist_email = article.email  # Use the email provided by the journalist

    if request.method == 'POST':
        action = request.POST.get('action')
        subject = f"Article Review Status: {article.title}"

        if action == 'accept':
            article.status = 'published'  # Change status to published
            article.save()

            # Send approval email
            message = f"Dear {article.author_name},\n\nYour article titled '{article.title}' has been approved and published by the editor."
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [journalist_email],
                fail_silently=False,
            )
            return redirect('editor:editor_dashboard')

        elif action == 'reject':
            article.status = 'rejected'
            article.save()

            # Send rejection email
            message = f"Dear {article.author_name},\n\nYour article titled '{article.title}' has been rejected by the editor."
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [journalist_email],
                fail_silently=False,
            )
            return redirect('editor:editor_dashboard')

    return render(request, 'review_article.html', {'article': article})



@role_required('editor')
def show_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'show_article.html', {'article': article})


@login_required
def article_review_list(request):
    articles = Article.objects.filter(is_published=False)
    return render(request, 'article_review_list.html', {'articles': articles})

