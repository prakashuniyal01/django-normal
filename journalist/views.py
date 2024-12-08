from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Article
from .forms import ArticleStep1Form, ArticleStep2Form
from head.forms import ArticleForm
from users.decorators import role_required
from django.apps import apps
from django.contrib.auth import logout as auth_logout
from django.conf import settings
from django.core.mail import send_mail

@role_required('journalist')
def journalist_dashboard(request):
    user = request.user

    # Fetch articles submitted by the journalist
    # submitted_articles = Article.objects.filter(email=user.email).order_by('-created_at')
    submitted_articles = Article.objects.filter(email=user.email).exclude(status='published').order_by('-created_at')

    # Fetch only published articles
    published_articles = Article.objects.filter(email=user.email, status='published').order_by('-created_at')

    full_name = f"{user.first_name} {user.last_name}"
    return render(request, 'journalist_dashboard.html', {
        'user': user,
        'submitted_articles': submitted_articles,
        'published_articles': published_articles,
    })


def j_logout(request):
    auth_logout(request)
    request.session.flush()

    return redirect('journalist:login_view')

@role_required('journalist')
def journalist_dashboard_step1(request):
    if request.method == 'POST':
        form = ArticleStep1Form(request.POST, user_email=request.user.email)
        print(form)
        if form.is_valid():
            request.session['article_data'] = form.cleaned_data
            return redirect('journalist:journalist_dashboard_step2')
    else:
        form = ArticleStep1Form(user_email=request.user.email)
    return render(request, 'journalist_dashboard_step1.html', {'form': form})

@role_required('journalist')
def journalist_dashboard_step2(request):
    if request.method == 'POST':
        form = ArticleStep2Form(request.POST, request.FILES)
        if form.is_valid():
            article_data = request.session.get('article_data', {})
            if not isinstance(article_data, dict):
                article_data = {}
            article_data.update(form.cleaned_data)

            tags = article_data.pop('tags', None)

            # No need to fetch or create the category; the form already provides it
            category = article_data['category']

            article = Article.objects.create(
                title=article_data.get('title'),
                subtitle=article_data.get('subtitle'),
                content=article_data.get('content'),
                author_name=article_data.get('author_name'),
                email=article_data.get('email'),
                image=article_data.get('image'),
                category=category,
                publish_date=article_data.get('publish_date'),
            )
            if tags:
                article.tags.set(tags)

            # Send email notification
            subject = f"New Article Submitted: {article.title}"
            message = (
                f"Dear Editor,\n\n"
                f"A new article titled '{article.title}' has been submitted by {article.author_name}.\n\n"
                f"Details:\n"
                f"Subtitle: {article.subtitle}\n"
                f"Category: {article.category}\n"
                f"Publish Date: {article.publish_date}\n\n"
                f"Best regards,\n"
                f"Your Article Management System"
            )
            journalist_email = article_data.get('email')
            editor_email = settings.EDITOR_EMAIL  # Define this in settings
            # editor_emails = [editor.email for editor in editor.objects.all()]

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [journalist_email, editor_email],
                fail_silently=False,
            )

            del request.session['article_data']
            return redirect('journalist:journalist_dashboard')
    else:
        form = ArticleStep2Form()
    article_data = request.session.get('article_data', {})
    for field in form.fields:
        form.fields[field].initial = article_data.get(field, None)
    return render(request, 'journalist_dashboard_step2.html', {'form': form})


@role_required('journalist')
def edit_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            print(f"Form is valid, saving article...")
            form.save()
            return redirect('journalist:journalist_dashboard')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'edit_article.html', {'form': form, 'article': article})




@role_required('journalist')
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.delete()
        return redirect('journalist_dashboard')
    return render(request, 'delete_article.html', {'article': article})

@role_required('journalist')
def show_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'show_article.html', {'article': article})

