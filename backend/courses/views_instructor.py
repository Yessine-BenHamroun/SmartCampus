"""
Instructor views for course management
"""
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from .models import Course, Enrollment, Review
from .extended_models import Module, Lesson, Quiz, Progress
from users.models import User


def is_instructor_or_admin(user):
    """Check if user has instructor or admin role"""
    # user is an AuthenticatedUser object with role attribute
    role = getattr(user, 'role', 'student')
    return role in ['instructor', 'admin']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    """Create a new course (instructors only)"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get course data
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category', 'general')
        level = request.data.get('level', 'beginner')
        price = float(request.data.get('price', 0))
        thumbnail = request.data.get('thumbnail', '')
        preview_video = request.data.get('preview_video', '')
        
        # Validate required fields
        if not title or not description:
            return Response({
                'error': 'Title and description are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create course
        course = Course.create(
            title=title,
            description=description,
            instructor_id=str(user.id),
            category=category,
            level=level,
            price=price,
            thumbnail=thumbnail,
            preview_video=preview_video,
            published=False  # Start as draft
        )
        
        return Response({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instructor_courses(request):
    """Get all courses created by the instructor"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Debug: Print user ID
        print(f"🔍 Fetching courses for instructor ID: {user.id}")
        
        # Get all courses by this instructor
        courses = Course.find_by_instructor(str(user.id))
        
        print(f"📚 Found {len(courses)} courses for instructor {user.id}")
        
        # Get enrollment counts for each course
        courses_with_stats = []
        for course in courses:
            course_dict = course.to_dict()
            print(f"  - Course: {course_dict['title']} (instructor_id: {course_dict.get('instructor_id')})")
            
            # Get enrollment count
            enrollments = Enrollment.find_by_course(course_dict['id'])
            course_dict['enrollment_count'] = len(enrollments)
            
            # Get module count
            modules = Module.find_by_course(course_dict['id'])
            course_dict['module_count'] = len(modules)
            
            # Get average rating
            reviews = Review.find_by_course(course_dict['id'])
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                course_dict['average_rating'] = round(avg_rating, 1)
                course_dict['review_count'] = len(reviews)
            else:
                course_dict['average_rating'] = 0
                course_dict['review_count'] = 0
            
            courses_with_stats.append(course_dict)
        
        return Response({
            'courses': courses_with_stats,
            'total': len(courses_with_stats)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Error fetching instructor courses: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_course(request, course_id):
    """Get, update, or delete a specific course"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get the course
        course = Course.find_by_id(course_id)
        if not course:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns this course (unless admin)
        if user.role != 'admin' and course.instructor_id != str(user.id):
            return Response({
                'error': 'You do not have permission to manage this course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            # Get course with modules and lessons
            course_dict = course.to_dict()
            
            # Get modules
            modules = Module.find_by_course(course_id)
            modules_with_lessons = []
            
            for module in modules:
                module_dict = module.to_dict()
                # Get lessons for this module
                lessons = Lesson.find_by_module(module_dict['id'])
                module_dict['lessons'] = [l.to_dict() for l in lessons]
                module_dict['lesson_count'] = len(lessons)
                modules_with_lessons.append(module_dict)
            
            course_dict['modules'] = modules_with_lessons
            course_dict['module_count'] = len(modules_with_lessons)
            
            return Response({
                'course': course_dict
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # Update course
            update_data = {}
            
            if 'title' in request.data:
                update_data['title'] = request.data['title']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            if 'category' in request.data:
                update_data['category'] = request.data['category']
            if 'level' in request.data:
                update_data['level'] = request.data['level']
            if 'price' in request.data:
                update_data['price'] = float(request.data['price'])
            if 'thumbnail' in request.data:
                update_data['thumbnail'] = request.data['thumbnail']
            if 'preview_video' in request.data:
                update_data['preview_video'] = request.data['preview_video']
            if 'published' in request.data:
                update_data['published'] = request.data['published']
            
            course.update(**update_data)
            
            return Response({
                'message': 'Course updated successfully',
                'course': course.to_dict()
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            # Delete course and all related data
            course.delete()
            
            # Delete all modules and lessons for this course
            modules = Module.find_by_course(course_id)
            for module in modules:
                module_id = module.to_dict()['id']
                # Delete lessons in this module
                lessons = Lesson.find_by_module(module_id)
                for lesson in lessons:
                    lesson.delete()
                module.delete()
            
            return Response({
                'message': 'Course deleted successfully'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_course_modules(request, course_id):
    """Get all modules with their lessons for a course"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        print(f"🔍 Fetching modules for course: {course_id}")
        
        # Verify course exists and user owns it
        course = Course.find_by_id(course_id)
        if not course:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if str(course.instructor_id) != str(user.id) and user.role != 'admin':
            return Response({
                'error': 'You do not have permission to access this course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all modules for this course
        modules = Module.find_by_course(course_id)
        print(f"📚 Found {len(modules)} modules")
        
        modules_with_lessons = []
        
        for module in modules:
            module_dict = module.to_dict()
            print(f"  - Module: {module_dict['title']} (ID: {module_dict['id']})")
            
            # Get lessons for this module
            lessons = Lesson.find_by_module(module_dict['id'])
            print(f"    Lessons: {len(lessons)}")
            module_dict['lessons'] = [lesson.to_dict() for lesson in lessons]
            
            modules_with_lessons.append(module_dict)
        
        return Response({
            'modules': modules_with_lessons,
            'total': len(modules_with_lessons)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_module(request, course_id):
    """Create a new module in a course"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Verify course exists and user owns it
        course = Course.find_by_id(course_id)
        if not course:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.role != 'admin' and course.instructor_id != str(user.id):
            return Response({
                'error': 'You do not have permission to add modules to this course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get module data
        title = request.data.get('title')
        description = request.data.get('description', '')
        order = request.data.get('order', 1)
        duration_minutes = request.data.get('duration_minutes', 0)
        
        # Validate required fields
        if not title:
            return Response({
                'error': 'Title is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create module
        module = Module.create(
            course_id=course_id,
            title=title,
            description=description,
            order=int(order),
            duration_minutes=int(duration_minutes),
            published=False
        )
        
        return Response({
            'message': 'Module created successfully',
            'module': module.to_dict()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_module(request, module_id):
    """Get, update, or delete a specific module"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get the module
        module = Module.find_by_id(module_id)
        if not module:
            return Response({
                'error': 'Module not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        module_dict = module.to_dict()
        
        # Verify user owns the course (unless admin)
        course = Course.find_by_id(module_dict['course_id'])
        if user.role != 'admin' and course.instructor_id != str(user.id):
            return Response({
                'error': 'You do not have permission to manage this module'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            # Get module with lessons
            lessons = Lesson.find_by_module(module_id)
            module_dict['lessons'] = [l.to_dict() for l in lessons]
            module_dict['lesson_count'] = len(lessons)
            
            return Response({
                'module': module_dict
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # Update module
            update_data = {}
            
            if 'title' in request.data:
                update_data['title'] = request.data['title']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            if 'order' in request.data:
                update_data['order'] = int(request.data['order'])
            if 'duration_minutes' in request.data:
                update_data['duration_minutes'] = int(request.data['duration_minutes'])
            if 'published' in request.data:
                update_data['published'] = request.data['published']
            
            module.update(**update_data)
            
            return Response({
                'message': 'Module updated successfully',
                'module': module.to_dict()
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            # Delete module and all lessons
            lessons = Lesson.find_by_module(module_id)
            for lesson in lessons:
                lesson.delete()
            
            module.delete()
            
            return Response({
                'message': 'Module deleted successfully'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def create_lesson(request, module_id):
    """Create a new lesson in a module"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Verify module exists
        module = Module.find_by_id(module_id)
        if not module:
            return Response({
                'error': 'Module not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        module_dict = module.to_dict()
        
        # Verify user owns the course
        course = Course.find_by_id(module_dict['course_id'])
        if user.role != 'admin' and course.instructor_id != str(user.id):
            return Response({
                'error': 'You do not have permission to add lessons to this module'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get lesson data (handle both JSON and FormData)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # FormData with files
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            content_type = request.POST.get('content_type', 'text')
            content = request.POST.get('content', '{}')
            duration_minutes = request.POST.get('duration_minutes', 0)
            is_free_preview = request.POST.get('is_free_preview', 'false').lower() == 'true'
            course_id = request.POST.get('course_id')
            
            # Parse content JSON
            import json
            try:
                content = json.loads(content)
            except:
                content = {}
            
            # Handle file uploads
            uploaded_files = request.FILES.getlist('files')
            resources = []
            
            for file in uploaded_files:
                # TODO: In production, upload to cloud storage (S3, Azure Blob, etc.)
                # For now, we'll store file info
                resources.append({
                    'name': file.name,
                    'size': file.size,
                    'type': file.content_type,
                    'url': f'/media/lessons/{file.name}'  # Placeholder
                })
        else:
            # JSON data
            title = request.data.get('title')
            description = request.data.get('description', '')
            content_type = request.data.get('content_type', 'text')
            content = request.data.get('content', {})
            duration_minutes = request.data.get('duration_minutes', 0)
            is_free_preview = request.data.get('is_free_preview', False)
            course_id = request.data.get('course_id')
            resources = request.data.get('resources', [])
        
        # Validate required fields
        if not title:
            return Response({
                'error': 'Title is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get current lesson count for order
        existing_lessons = Lesson.find_by_module(module_id)
        order = len(existing_lessons) + 1
        
        # Create lesson
        lesson = Lesson.create(
            module_id=module_id,
            course_id=course_id or module_dict['course_id'],
            title=title,
            description=description,
            content_type=content_type,
            content=content,
            order=order,
            duration_minutes=int(duration_minutes),
            is_free_preview=is_free_preview,
            resources=resources,
            is_published=False
        )
        
        return Response({
            'message': 'Lesson created successfully',
            'lesson': lesson.to_dict()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ Error creating lesson: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_lesson(request, lesson_id):
    """Get, update, or delete a specific lesson"""
    user = request.user
    
    # Check if user is instructor or admin
    if not is_instructor_or_admin(user):
        return Response({
            'error': 'Access denied. Instructor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get the lesson
        lesson = Lesson.find_by_id(lesson_id)
        if not lesson:
            return Response({
                'error': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        lesson_dict = lesson.to_dict()
        
        # Verify user owns the course
        course = Course.find_by_id(lesson_dict['course_id'])
        if user.role != 'admin' and course.instructor_id != str(user.id):
            return Response({
                'error': 'You do not have permission to manage this lesson'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            return Response({
                'lesson': lesson_dict
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # Update lesson
            update_data = {}
            
            if 'title' in request.data:
                update_data['title'] = request.data['title']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            if 'lesson_type' in request.data:
                update_data['lesson_type'] = request.data['lesson_type']
            if 'content' in request.data:
                update_data['content'] = request.data['content']
            if 'video_url' in request.data:
                update_data['video_url'] = request.data['video_url']
            if 'duration_minutes' in request.data:
                update_data['duration_minutes'] = int(request.data['duration_minutes'])
            if 'order' in request.data:
                update_data['order'] = int(request.data['order'])
            if 'resources' in request.data:
                update_data['resources'] = request.data['resources']
            if 'published' in request.data:
                update_data['published'] = request.data['published']
            
            lesson.update(**update_data)
            
            return Response({
                'message': 'Lesson updated successfully',
                'lesson': lesson.to_dict()
            }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            lesson.delete()
            
            return Response({
                'message': 'Lesson deleted successfully'
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
