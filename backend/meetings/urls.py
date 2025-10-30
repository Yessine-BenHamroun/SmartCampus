"""
Meeting URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # Meeting CRUD
    path('', views.meeting_list, name='meeting-list'),  # GET: list, POST: create
    path('<str:meeting_id>/', views.meeting_detail, name='meeting-detail'),  # GET, PUT, DELETE
    
    # Meeting actions
    path('<str:meeting_id>/start/', views.meeting_start, name='meeting-start'),
    path('<str:meeting_id>/end/', views.meeting_end, name='meeting-end'),
    path('<str:meeting_id>/join/', views.meeting_join, name='meeting-join'),
    path('<str:meeting_id>/leave/', views.meeting_leave, name='meeting-leave'),
    path('<str:meeting_id>/respond/', views.meeting_respond, name='meeting-respond'),
    
    # Student meetings
    path('my/invitations/', views.student_meetings, name='student-meetings'),
]
