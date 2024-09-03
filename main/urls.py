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
    path('admin_user_profile/<int:user_id>/', views.admin_profile, name='admin_profile'),
    path('admin_learning-materials/', views.admin_learning_materials, name='admin_learning_materials'),
    path('admin_learning-materials/create/', views.create_learning_material, name='create_learning_material'),
    path('admin_learning-materials/<int:material_id>/update/', views.update_learning_material, name='update_learning_material'),
    path('admin_learning-materials/<int:material_id>/delete/', views.delete_learning_material, name='delete_learning_material'),
    path('admin_learning-materials/preview/<int:material_id>/', views.preview_material, name='preview_material'),


    # path('dashboard/', user_home, name='user_home'),
    path('dashboard/', views.user_home, name='user_home'),
    path('quizzes/', views.quizzes, name='quizzes'),
    path('quiz/start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/continue/<int:attempt_id>/', views.continue_quiz, name='continue_quiz'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),

]