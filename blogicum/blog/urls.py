from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<slug:username>/', views.UserProfileListView.as_view(), name='profile'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('category/<slug:category_slug>/',
         views.PostCategoryListView.as_view(), name='category_posts'),
]
