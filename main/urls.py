from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_topics/', views.admin_topics, name='admin_topics'),  
    path('admin_quizzes/', views.admin_quizzes, name='admin_quizzes'),
    path('admin_quizzes/create/', views.create_quiz, name='create_quiz'),
    path('admin_quizzes/<int:quiz_id>/add-questions/', views.add_questions, name='add_questions'),
    path('admin_quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('admin_quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'), 
    path('admin_user_statistics/', views.user_statistics, name='user_statistics'),
    path('admin_user_profile/<int:user_id>/', views.user_profile, name='user_profile'),

    # path('dashboard/', user_dashboard, name='user_dashboard'),
]