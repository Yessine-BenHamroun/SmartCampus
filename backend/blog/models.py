"""
Blog post models for MongoDB
"""
from datetime import datetime
from bson import ObjectId
from config.mongodb import get_collection


class BlogPost:
    """Blog post model"""
    
    COLLECTION_NAME = 'blog_posts'
    
    CATEGORIES = ['Technology', 'Education', 'Career', 'Tips & Tricks', 
                  'News', 'Student Life', 'Industry Insights']
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.title = kwargs.get('title')
        self.slug = kwargs.get('slug')
        self.content = kwargs.get('content')
        self.excerpt = kwargs.get('excerpt', '')
        self.author_id = kwargs.get('author_id')  # Reference to User
        self.category = kwargs.get('category')
        self.tags = kwargs.get('tags', [])
        self.featured_image = kwargs.get('featured_image', '')
        self.is_published = kwargs.get('is_published', False)
        self.is_featured = kwargs.get('is_featured', False)
        self.views_count = kwargs.get('views_count', 0)
        self.likes_count = kwargs.get('likes_count', 0)
        self.comments_count = kwargs.get('comments_count', 0)
        self.published_at = kwargs.get('published_at')
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(BlogPost.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create blog post"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        kwargs['views_count'] = 0
        kwargs['likes_count'] = 0
        kwargs['comments_count'] = 0
        
        if kwargs.get('is_published') and not kwargs.get('published_at'):
            kwargs['published_at'] = datetime.utcnow()
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_id(cls, post_id):
        """Find post by ID"""
        collection = cls.get_collection()
        if isinstance(post_id, str):
            post_id = ObjectId(post_id)
        post_data = collection.find_one({'_id': post_id})
        return cls(**post_data) if post_data else None
    
    @classmethod
    def find_by_slug(cls, slug):
        """Find post by slug"""
        collection = cls.get_collection()
        post_data = collection.find_one({'slug': slug, 'is_published': True})
        return cls(**post_data) if post_data else None
    
    @classmethod
    def find_all(cls, filters=None, skip=0, limit=10):
        """Find all posts with filters"""
        collection = cls.get_collection()
        query = filters or {'is_published': True}
        posts_data = collection.find(query).skip(skip).limit(limit).sort('published_at', -1)
        return [cls(**post) for post in posts_data]
    
    @classmethod
    def find_by_author(cls, author_id):
        """Find posts by author"""
        collection = cls.get_collection()
        if isinstance(author_id, str):
            author_id = ObjectId(author_id)
        posts_data = collection.find({'author_id': author_id}).sort('created_at', -1)
        return [cls(**post) for post in posts_data]
    
    @classmethod
    def find_featured(cls, limit=3):
        """Find featured posts"""
        collection = cls.get_collection()
        posts_data = collection.find({'is_featured': True, 'is_published': True}).limit(limit)
        return [cls(**post) for post in posts_data]
    
    def update(self, **kwargs):
        """Update post"""
        collection = self.get_collection()
        kwargs['updated_at'] = datetime.utcnow()
        
        # Set published_at if publishing for first time
        if kwargs.get('is_published') and not self.published_at:
            kwargs['published_at'] = datetime.utcnow()
        
        collection.update_one({'_id': self.id}, {'$set': kwargs})
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def increment_views(self):
        """Increment view count"""
        collection = self.get_collection()
        collection.update_one({'_id': self.id}, {'$inc': {'views_count': 1}})
        self.views_count += 1
    
    def delete(self):
        """Delete post"""
        collection = self.get_collection()
        collection.delete_one({'_id': self.id})
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'slug': self.slug,
            'content': self.content,
            'excerpt': self.excerpt,
            'author_id': str(self.author_id) if self.author_id else None,
            'category': self.category,
            'tags': self.tags,
            'featured_image': self.featured_image,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class BlogComment:
    """Blog comment model"""
    
    COLLECTION_NAME = 'blog_comments'
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id')
        self.post_id = kwargs.get('post_id')
        self.user_id = kwargs.get('user_id')
        self.content = kwargs.get('content')
        self.parent_id = kwargs.get('parent_id')  # For nested comments
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @staticmethod
    def get_collection():
        return get_collection(BlogComment.COLLECTION_NAME)
    
    @classmethod
    def create(cls, **kwargs):
        """Create comment"""
        collection = cls.get_collection()
        kwargs['created_at'] = datetime.utcnow()
        kwargs['updated_at'] = datetime.utcnow()
        
        result = collection.insert_one(kwargs)
        kwargs['_id'] = result.inserted_id
        return cls(**kwargs)
    
    @classmethod
    def find_by_post(cls, post_id):
        """Find comments by post"""
        collection = cls.get_collection()
        if isinstance(post_id, str):
            post_id = ObjectId(post_id)
        comments_data = collection.find({'post_id': post_id}).sort('created_at', -1)
        return [cls(**comment) for comment in comments_data]
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'post_id': str(self.post_id),
            'user_id': str(self.user_id),
            'content': self.content,
            'parent_id': str(self.parent_id) if self.parent_id else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
