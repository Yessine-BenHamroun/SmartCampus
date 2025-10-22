"""
Blog API views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from bson import ObjectId

from blog.models import BlogPost, BlogComment
from blog.serializers import BlogPostSerializer, BlogCommentSerializer
from users.models import User


class BlogPostListView(APIView):
    """List all blog posts or create a new post"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all blog posts with optional filters"""
        try:
            category = request.query_params.get('category')
            tag = request.query_params.get('tag')
            search = request.query_params.get('search')
            featured = request.query_params.get('featured')
            skip = int(request.query_params.get('skip', 0))
            limit = int(request.query_params.get('limit', 10))
            
            filters = {'is_published': True}
            if category:
                filters['category'] = category
            if tag:
                filters['tags'] = tag
            if featured:
                filters['is_featured'] = featured.lower() == 'true'
            if search:
                filters['$or'] = [
                    {'title': {'$regex': search, '$options': 'i'}},
                    {'content': {'$regex': search, '$options': 'i'}}
                ]
            
            posts = BlogPost.find_all(filters, skip, limit)
            
            posts_data = []
            for post in posts:
                post_dict = post.to_dict()
                
                # Get author details
                if post.author_id:
                    author = User.find_by_id(post.author_id)
                    if author:
                        post_dict['author'] = {
                            'id': str(author.id),
                            'name': f"{author.first_name} {author.last_name}",
                            'profile_image': author.profile_image
                        }
                
                posts_data.append(post_dict)
            
            return Response({
                'count': len(posts_data),
                'posts': posts_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch blog posts',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create a new blog post"""
        try:
            user_id = request.user.get('user_id')
            user = User.find_by_id(user_id)
            
            if not user or user.role not in ['instructor', 'admin']:
                return Response({
                    'error': 'Only instructors and admins can create blog posts'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = BlogPostSerializer(data=request.data)
            
            if serializer.is_valid():
                post_data = serializer.validated_data.copy()
                post_data['author_id'] = ObjectId(user_id)
                
                post = BlogPost.create(**post_data)
                
                return Response({
                    'message': 'Blog post created successfully',
                    'post': post.to_dict()
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create blog post',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogPostDetailView(APIView):
    """Get, update, or delete a specific blog post"""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get blog post by slug"""
        try:
            post = BlogPost.find_by_slug(slug)
            
            if not post:
                return Response({
                    'error': 'Blog post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Increment views
            post.increment_views()
            
            post_dict = post.to_dict()
            
            # Get author details
            if post.author_id:
                author = User.find_by_id(post.author_id)
                if author:
                    post_dict['author'] = {
                        'id': str(author.id),
                        'name': f"{author.first_name} {author.last_name}",
                        'email': author.email,
                        'bio': author.bio,
                        'profile_image': author.profile_image
                    }
            
            # Get comments
            comments = BlogComment.find_by_post(post.id)
            comments_data = []
            for comment in comments:
                comment_dict = comment.to_dict()
                user = User.find_by_id(comment.user_id)
                if user:
                    comment_dict['user'] = {
                        'id': str(user.id),
                        'name': f"{user.first_name} {user.last_name}",
                        'profile_image': user.profile_image
                    }
                comments_data.append(comment_dict)
            
            post_dict['comments'] = comments_data
            
            return Response({
                'post': post_dict
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch blog post',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, slug):
        """Update blog post"""
        try:
            post = BlogPost.find_by_slug(slug)
            
            if not post:
                return Response({
                    'error': 'Blog post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            user_id = request.user.get('user_id')
            if str(post.author_id) != user_id:
                return Response({
                    'error': 'Only author can update this post'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = BlogPostSerializer(data=request.data, partial=True)
            
            if serializer.is_valid():
                post.update(**serializer.validated_data)
                
                return Response({
                    'message': 'Blog post updated successfully',
                    'post': post.to_dict()
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to update blog post',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, slug):
        """Delete blog post"""
        try:
            post = BlogPost.find_by_slug(slug)
            
            if not post:
                return Response({
                    'error': 'Blog post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            user_id = request.user.get('user_id')
            if str(post.author_id) != user_id:
                return Response({
                    'error': 'Only author can delete this post'
                }, status=status.HTTP_403_FORBIDDEN)
            
            post.delete()
            
            return Response({
                'message': 'Blog post deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to delete blog post',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogCommentView(APIView):
    """Create a comment on a blog post"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        """Create a comment"""
        try:
            user_id = request.user.get('user_id')
            
            # Check if post exists
            post = BlogPost.find_by_id(post_id)
            if not post:
                return Response({
                    'error': 'Blog post not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = BlogCommentSerializer(data=request.data)
            
            if serializer.is_valid():
                comment_data = serializer.validated_data.copy()
                comment_data['user_id'] = ObjectId(user_id)
                comment_data['post_id'] = ObjectId(post_id)
                
                comment = BlogComment.create(**comment_data)
                
                # Update post comments count
                post.update(comments_count=post.comments_count + 1)
                
                return Response({
                    'message': 'Comment created successfully',
                    'comment': comment.to_dict()
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create comment',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeaturedBlogPostsView(APIView):
    """Get featured blog posts"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get featured blog posts"""
        try:
            limit = int(request.query_params.get('limit', 3))
            posts = BlogPost.find_featured(limit)
            
            posts_data = []
            for post in posts:
                post_dict = post.to_dict()
                
                # Get author details
                if post.author_id:
                    author = User.find_by_id(post.author_id)
                    if author:
                        post_dict['author'] = {
                            'id': str(author.id),
                            'name': f"{author.first_name} {author.last_name}",
                            'profile_image': author.profile_image
                        }
                
                posts_data.append(post_dict)
            
            return Response({
                'count': len(posts_data),
                'posts': posts_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch featured posts',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthorPostsView(APIView):
    """Get blog posts by author"""
    permission_classes = [AllowAny]
    
    def get(self, request, author_id):
        """Get all posts by an author"""
        try:
            posts = BlogPost.find_by_author(author_id)
            posts_data = [post.to_dict() for post in posts if post.is_published]
            
            return Response({
                'count': len(posts_data),
                'posts': posts_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to fetch author posts',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
