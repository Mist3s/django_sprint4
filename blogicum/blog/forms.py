from django import forms
from django.utils import timezone

from .models import Post, Comment, User


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        label='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
                  '— можно делать отложенные публикации.',
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        ),
        initial=timezone.now
    )

    class Meta:
        model = Post
        exclude = ('author', 'is_published')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': '3'}
            )
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
