from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.utils import timezone

from .models import Post

POST_LIMIT = 5


def get_query_set_post():
    query_set_post = Post.objects.select_related(
        'category',
        'location',
        'author',
    ).filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    )
    return query_set_post


def index(request):
    template = 'blog/index.html'
    post_list = get_query_set_post()[:POST_LIMIT]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(
        get_query_set_post(),
        pk=pk
    )
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    post_list = get_list_or_404(
        get_query_set_post().filter(
            category__slug=category_slug,
        )
    )
    context = {
        'post_list': post_list,
        'category': post_list[0].category,
    }
    return render(request, template, context)
