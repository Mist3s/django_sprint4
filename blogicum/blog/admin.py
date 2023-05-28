from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'is_published',
        'pub_date',
        'category',
        'author',
        'location'
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


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
