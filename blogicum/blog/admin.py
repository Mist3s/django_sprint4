from django.contrib import admin

from .models import (
    Category, Location, Post, Comment
)


@admin.display(description='Текст комментария')
def trim_field_text(obj):
    return u"%s..." % (obj.text[:150],)


# Count('comments')
@admin.display(description='Комментариев')
def comment_count(obj):
    return obj.comments.count()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'is_published',
        'pub_date',
        'category',
        'author',
        'location',
        comment_count
    )
    list_editable = (
        'category',
        'is_published',
        'author',
        'location'
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'category',
        'is_published',
        'author',
        'location'
    )
    list_display_links = (
        'title',
    )
    ordering = (
        '-id',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'slug',
    )
    list_editable = (
        'is_published',
        'slug',
    )
    search_fields = (
        'title',
    )
    list_filter = (
        'is_published',
    )
    list_display_links = (
        'title',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'is_published',
    )
    list_display_links = (
        'name',
    )
    empty_value_display = 'Не задано'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        trim_field_text,
        'post',
        'created_at'
    )
    list_filter = (
        'created_at',
        'author',
        'post'
    )
    search_fields = (
        'text',
    )
    ordering = (
        '-created_at',
    )
