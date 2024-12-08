from datetime import timezone
from django import forms
from .models import Article, Tag,Comment,Category
from django.utils import timezone

class ArticleStep1Form(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content', 'author_name', 'email']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title
    
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)  # Pop the email from the keyword arguments
        super().__init__(*args, **kwargs)
        if user_email:
            self.fields['email'].initial = user_email
            
class ArticleStep2Form(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['image', 'tags', 'category', 'publish_date']

    TAG_CHOICES = [
        ('politics', 'Politics'),
        ('tech', 'Tech'),
        ('sports', 'Sports'),
        ('fun', 'Fun'),
    ]

    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('opinion', 'Opinion'),
        ('trends', 'Trends'),
    ]

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Tags",
        required=True  # Ensure at least one tag is required
    )
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    publish_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))  # Added type="date" for the input
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['publish_date'].widget.attrs['min'] = today.isoformat()

    def clean_publish_date(self):
        publish_date = self.cleaned_data.get('publish_date')
        if publish_date <= timezone.now().date():
            raise forms.ValidationError("Publish date must be in the future.")
        return publish_date

    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'})
        }
