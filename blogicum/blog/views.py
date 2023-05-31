from django.db.models import Count
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from .models import Post, User, Comment
from .forms import PostForm, CommentForm

POST_LIMIT = 10


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


# def index(request):
#     template = 'blog/index.html'
#     post_list = get_query_set_post()[:POST_LIMIT]
#     context = {'post_list': post_list}
#     return render(request, template, context)


class PostListView(ListView):
    model = Post
    paginate_by = POST_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )


# def post_detail(request, pk):
#     template = 'blog/detail.html'
#     post = get_object_or_404(
#         get_query_set_post(),
#         pk=pk
#     )
#     context = {'post': post}
#     return render(request, template, context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True
        )


# def category_posts(request, category_slug):
#     template = 'blog/category.html'
#     post_list = get_list_or_404(
#         get_query_set_post().filter(
#             category__slug=category_slug,
#         )
#     )
#     context = {
#         'post_list': post_list,
#         'category': post_list[0].category,
#     }
#     return render(request, template, context)


class PostCategoryListView(ListView):
    model = Post
    paginate_by = POST_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            is_published=True,
            pub_date__lt=timezone.now(),
            category__is_published=True,
            # category__slug=self.category_slug,
        )

        return queryset


class UserProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'pub_date'
    paginate_by = POST_LIMIT
    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.profile = get_object_or_404(
            User, username=kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        profile = self.kwargs['username']
        queryset = Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            author__username=profile
        )
        if not self.request.user.username == profile:
            queryset = queryset.filter(
                is_published=True,
                pub_date__lt=timezone.now(),
                category__is_published=True
            )

        return queryset.annotate(Count('author'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User.objects.get(
            username=self.kwargs['username']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        # Получаем объект по первичному ключу и автору или вызываем 404 ошибку.
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        # Если объект был найден, то вызываем родительский метод,
        # чтобы работа CBV продолжилась.
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    post = None
    model = Comment
    form_class = CommentForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['pk'])
        print(self.post)
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        # form.instance.post = self.post

        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post.pk})
