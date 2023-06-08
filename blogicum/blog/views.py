from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, get_list_or_404
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, DeleteView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from .models import Post, User, Comment, Category
from .forms import PostForm, CommentForm, UserUpdateForm

POST_LIMIT = 10


class VerificationAuthorBaseClass(LoginRequiredMixin):
    model = Post

    def dispatch(self, request, *args, **kwargs):
        model_pk = 'pk'
        if self.model == Post:
            model_pk = 'post_id'
        instance = get_object_or_404(self.model, pk=kwargs[model_pk])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


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


class PostListView(ListView):
    model = Post
    paginate_by = POST_LIMIT
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = get_query_set_post().order_by('-pub_date')
        return queryset.annotate(comment_count=Count('comments'))


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_queryset(self):
        return get_query_set_post().filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCategoryListView(ListView):
    model = Post
    paginate_by = POST_LIMIT
    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_list_or_404(Category.objects.filter(
                slug=self.kwargs['category_slug'],
                is_published=True
            ).prefetch_related(
                Prefetch(
                    'post_set',
                    get_query_set_post().filter(
                        category__slug=self.kwargs['category_slug'],
                    ).annotate(
                            comment_count=Count('comments')
                        ).order_by('-pub_date'),
                    'post_list'
                )
            )
        )
        return self.category[0].post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category[0]
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    ordering = 'pub_date'
    paginate_by = POST_LIMIT
    profile = None

    def get_queryset(self):
        queryset = Post.objects.filter(
            author__username=self.kwargs['username']
        )
        if self.request.user.username != self.kwargs['username']:
            queryset = Post.objects.filter(
                author__username=self.kwargs['username'],
                is_published=True,
                pub_date__lt=timezone.now(),
                category__is_published=True
            )
        self.profile = get_object_or_404(
            User.objects.filter(
                username=self.kwargs['username']
            ).prefetch_related(
                Prefetch(
                    'post_set',
                    queryset.annotate(
                        comment_count=Count('comments')
                    ).order_by('-pub_date'),
                    'post_list'
                )
            )
        )

        return self.profile.post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserUpdateForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(VerificationAuthorBaseClass, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDeleteView(VerificationAuthorBaseClass, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_obj = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(VerificationAuthorBaseClass, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(VerificationAuthorBaseClass, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['post_id']}
        )
