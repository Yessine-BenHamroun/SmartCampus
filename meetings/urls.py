from django.urls import path
from . import views

urlpatterns = [
    # Vues instructeur
    path('', views.meeting_list, name='meeting_list'),
    path('create/', views.meeting_create, name='meeting_create'),
    path('<uuid:pk>/', views.meeting_detail, name='meeting_detail'),
    path('<uuid:pk>/edit/', views.meeting_update, name='meeting_update'),
    path('<uuid:pk>/delete/', views.meeting_delete, name='meeting_delete'),
    path('<uuid:pk>/start/', views.meeting_start, name='meeting_start'),
    path('<uuid:pk>/end/', views.meeting_end, name='meeting_end'),
    
    # Vues étudiant
    path('my-meetings/', views.student_meetings, name='student_meetings'),
    path('<uuid:pk>/join/', views.meeting_join, name='meeting_join'),
    path('<uuid:pk>/respond/<str:action>/', views.meeting_respond, name='meeting_respond'),
    
    # Salle de réunion
    path('<uuid:pk>/room/', views.meeting_room, name='meeting_room'),
    path('<uuid:pk>/leave/', views.meeting_leave, name='meeting_leave'),
]
