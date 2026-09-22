from django import forms

from articles.models import Article, Rating


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'image', 'category', 'content']
        labels = {
            'title': 'Title',
            'image': 'Cover image',
            'category': 'Category',
            'content': 'Content',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Article title',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your article here',
                'rows': 12,
            }),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty")
        return title

    def clean_content(self):
        content = self.cleaned_data['content'].strip()
        if len(content) < 50:
            raise forms.ValidationError("Article content must be at least 50 characters long")
        return content


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.Select(attrs={'class': 'form-select'}),
        }
