from django.contrib.auth import login as auth_login, logout as auth_logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from journalist.models import Article, Like, Comment
from journalist.forms import CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def home(request):
    return render(request, 'users/home.html')

# def update_profile(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST,request.FILES, instance=request.user.userprofile)
#         if form.is_valid():
#             form.save()
#             return redirect('users:user_profile')  # Redirect after successful update
#     else:
#         form = CustomUserCreationForm(instance=request.user.userprofile)
    
#     return render(request, 'user_profile.html', {'form': form})

from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile

def update_profile(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:user_profile')  # Redirect after successful update
    else:
        user_form = CustomUserCreationForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
    
    return render(request, 'update_profile.html', {'user_form': user_form, 'profile_form': profile_form})



# views.py

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .models import CustomUser

@login_required
def user_profile_view(request):
    user = request.user

    if request.method == 'POST':
        # Handle profile update
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validate fields
        if not first_name or not last_name:
            messages.error(request, 'First name and last name cannot be empty.')
        else:
            # Update user's first and last name
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Show success message and log the change
            messages.success(request, 'Your profile has been updated.')
            logger.debug("Profile updated successfully.")

            # Redirect to the same page to show the updated info
            return redirect('user_profile')

    # Render the profile page with user info
    return render(request, 'user_profile.html', {'user': user})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in after password change
            messages.success(request, 'Your password has been updated.')
            return redirect('user_profile')  # Redirect after successful password change
        # else:
        #     # logger.debug(f"Form errors: {form.errors}")  # Debugging logs
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'user_profile.html', {'password_form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password, backend='users.backends.CustomBackend')

            if user is not None:
                print(f'User Role: Viewer = {user.is_viewer},Journalist={user.is_journalist}, Editor={user.is_editor}, Head={user.is_head}')
                auth_login(request, user)
                if user.is_journalist:
                    return redirect('journalist_dashboard')
                elif user.is_editor:
                    return redirect('editor_dashboard')
                elif user.is_head:
                    return redirect('head_dashboard')
                elif user.is_viewer:
                    return redirect('dashboard')               
                else:
                    return redirect('login_view')

            else:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    request.session.flush()

    return redirect('login')



class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'  # Template for email submission
    email_template_name = 'users/password_reset_email.html'  # Email sent to users
    subject_template_name = 'users/password_reset_subject.txt'  # Email subject
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    success_message = "An email has been sent to reset your password. Please check your inbox."

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')



class ArticleListView(ListView):
    model = Article
    template_name = 'dashboard.html'
    context_object_name = 'articles'
    ordering = ['-publish_date']

    def get_queryset(self):
        # Filter to show only published articles
        return Article.objects.filter(status='published').order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for article in context['articles']:
            # Add the last comment and its author for each article
            last_comment = article.comments.last()
            if last_comment:
                article.last_comment = last_comment.content
                article.commenter = last_comment.user.username
            else:
                article.last_comment = None
                article.commenter = None
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    like, created = Like.objects.get_or_create(article=article, user=request.user)
    if not created:
        like.delete()
    return JsonResponse({"likes_count": article.likes.count()})

@login_required
def add_comment(request, pk):
    article = get_object_or_404(Article, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
    return redirect('dashboard')

