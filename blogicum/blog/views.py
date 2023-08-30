from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, DeleteView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

from .models import Post, User, Comment, Category
from .forms import PostForm, CommentForm, UserUpdateForm
from .serializers import PostSerializer

POST_LIMIT = 10


class APIPostLowLevel(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIPostDetailLowLevel(APIView):
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404

    def get(self, *args, **kwargs):
        post = self.get_object(self.kwargs['pk'])
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        post = self.get_object(self.kwargs['pk'])
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        post = self.get_object(self.kwargs['pk'])
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, *args, **kwargs):
        post = self.get_object(self.kwargs['pk'])
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_post(request, pk):
    if request.method == 'GET':
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post)
        return JsonResponse(serializer.data, safe=False)


class APIPostList(generics.ListCreateAPIView):
    """'GET', 'POST'"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class APIPostDetail(generics.RetrieveUpdateDestroyAPIView):
    """'GET', 'PUT', 'PATCH', 'DELETE'"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer


@api_view(['GET', 'POST'])
def api_posts(request):
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def api_posts_detail(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'PUT' or request.method == 'PATCH':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    serializer = PostSerializer(post)
    return Response(serializer.data)


class VerificationAuthorBaseClass:
    model = Post

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(self.model, pk=kwargs[self.pk_url_kwarg])
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
        self.category = get_object_or_404(
            Category.objects.filter(
                slug=self.kwargs['category_slug'],
                is_published=True
            ).prefetch_related(
                Prefetch(
                    'post_set',
                    get_query_set_post().annotate(
                        comment_count=Count('comments')
                    ).order_by('-pub_date'),
                    'post_list'
                )
            )
        )
        return self.category.post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
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
                Q(author__username=self.kwargs['username'])
                & Q(is_published=True)
                & Q(pub_date__lt=timezone.now())
                & Q(category__is_published=True)
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
