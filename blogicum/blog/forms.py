from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    # Удаляем все описания полей.

    # Все настройки задаём в подклассе Meta.
    class Meta:
        # Указываем модель, на основе которой должна строиться форма.
        model = Post
        # Указываем, что надо отобразить все поля.
        # fields = '__all__'
        exclude = ('author', 'is_published')

        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }
