"""
Blog app URL configuration
"""
from django.urls import path
from blog.views import (
    BlogPostListView,
    BlogPostDetailView,
    BlogCommentView,
    FeaturedBlogPostsView,
    AuthorPostsView
)

app_name = 'blog'

urlpatterns = [
    # Blog posts
    path('', BlogPostListView.as_view(), name='post-list'),
    path('featured/', FeaturedBlogPostsView.as_view(), name='featured-posts'),
    path('author/<str:author_id>/', AuthorPostsView.as_view(), name='author-posts'),
    path('<slug:slug>/', BlogPostDetailView.as_view(), name='post-detail'),
    
    # Comments
    path('<str:post_id>/comments/', BlogCommentView.as_view(), name='post-comments'),
]
