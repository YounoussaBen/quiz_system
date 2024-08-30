from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import Quiz, User, UserQuizAttempt, Topic, UserBadge
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import TopicForm, QuizForm, QuestionForm, OptionFormSet
from django.http import JsonResponse

def logout_view(request):
    logout(request)
    return redirect('login') 
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'user/register.html')
        
        try:
            user = User.objects.create_user(email=email, password=password)
            login(request, user)
            return redirect('user_dashboard')
        except IntegrityError:
            messages.error(request, 'Email already exists')
        except ValueError as e:
            messages.error(request, str(e))
    
    return render(request, 'user/register.html')



def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get statistics
    active_users = User.objects.filter(is_active=True, is_staff=False).count()

    # Get recent activities
    recent_quizzes = Quiz.objects.select_related('created_by').order_by('-created_at')[:5]


    # Get the current admin user
    admin_user = request.user

    # Calculate the number of topics created by the admin user
    topics = Topic.objects.filter(created_by=admin_user).count()

    # Calculate the number of quizzes created by the admin user
    quizzes = Quiz.objects.filter(created_by=admin_user).count()

    context = {
        'active_users': active_users,
        'recent_quizzes': recent_quizzes,
        'topics': topics, 
        'quizzes': quizzes, 
    }

    return render(request, 'admin/admin_dashboard.html', context)


@user_passes_test(is_admin)
def admin_topics(request):
    topics = Topic.objects.all().order_by('-created_at')
    form = TopicForm()

    if request.method == 'POST':
        if 'add' in request.POST:
            form = TopicForm(request.POST)
            if form.is_valid():
                topic = form.save(commit=False)
                topic.created_by = request.user
                topic.save()
                messages.success(request, 'Topic added successfully.')
                return redirect('admin_topics')
        elif 'edit' in request.POST:
            topic_id = request.POST.get('topic_id')
            topic = get_object_or_404(Topic, id=topic_id)
            form = TopicForm(request.POST, instance=topic)
            if form.is_valid():
                form.save()
                messages.success(request, 'Topic updated successfully.')
                return redirect('admin_topics')
        elif 'delete' in request.POST:
            topic_id = request.POST.get('topic_id')
            topic = get_object_or_404(Topic, id=topic_id)
            topic.delete()
            messages.success(request, 'Topic deleted successfully.')
            return redirect('admin_topics')

    context = {
        'topics': topics,
        'form': form,
    }
    return render(request, 'admin/admin_topics.html', context)

@user_passes_test(is_admin)
def admin_quizzes(request):
    topics = Topic.objects.all()
    selected_topic = request.GET.get('topic')
    quizzes = Quiz.objects.all().order_by('-created_at')
    
    if selected_topic:
        quizzes = quizzes.filter(topic_id=selected_topic)

    context = {
        'topics': topics,
        'quizzes': quizzes,
        'selected_topic': selected_topic,
    }
    return render(request, 'admin/admin_quizzes.html', context)

@user_passes_test(is_admin)
def create_quiz(request):
    if request.method == 'POST':
        quiz_form = QuizForm(request.POST)
        if quiz_form.is_valid():
            quiz = quiz_form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, 'Quiz created successfully. Now add questions.')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        quiz_form = QuizForm()

    return render(request, 'admin/create_quiz.html', {'form': quiz_form})

@user_passes_test(is_admin)
def add_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            option_formset = OptionFormSet(request.POST, instance=question)
            if option_formset.is_valid():
                option_formset.save()
                
            messages.success(request, 'Question added successfully.')
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        option_formset = OptionFormSet()

    context = {
        'quiz': quiz,
        'question_form': question_form,
        'option_formset': option_formset,
    }
    return render(request, 'admin/add_questions.html', context)

@user_passes_test(is_admin)
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully.')
            return redirect('admin_quizzes')
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'admin/edit_quiz.html', {'form': form, 'quiz': quiz})

@user_passes_test(is_admin)
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully.')
        return redirect('admin_quizzes')
    return render(request, 'admin/delete_quiz.html', {'quiz': quiz})

@user_passes_test(is_admin)
def user_statistics(request):
    users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-level', '-total_score')
    
    context = {
        'users': users,
    }
    return render(request, 'admin/user_statistics.html', context)

@user_passes_test(is_admin)
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    quiz_attempts = UserQuizAttempt.objects.filter(user=user)
    badges = UserBadge.objects.filter(user=user)
    
    # Serialize user data
    user_data = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'total_score': user.total_score,
        'level': user.level,
    }
    
    # Serialize quiz attempts data
    quiz_attempts_data = [
        {
            'quiz_id': attempt.quiz.id,
            'quiz_title': attempt.quiz.title,
            'score': attempt.score,
        }
        for attempt in quiz_attempts
    ]
    
    # Serialize badges data
    badges_data = [
        {
            'badge_name': badge.badge.name,
            'badge_image': badge.badge.icon if badge.badge.icon else None 
        }
        for badge in badges
    ]
    
    # Calculate average score
    avg_score = quiz_attempts.aggregate(Avg('score'))['score__avg']
    
    context = {
        'profile_user': user_data,
        'quiz_attempts': quiz_attempts_data,
        'badges': badges_data,
        'avg_score': avg_score,
    }
    
    return JsonResponse(context)



# @login_required
# def user_dashboard(request):
#     user = request.user

#     # Get today's quiz
#     todays_quiz = Quiz.objects.filter(is_active=True).order_by('?').first()

#     # Get user statistics
#     total_points = UserQuizAttempt.objects.filter(user=user).aggregate(Sum('score'))['score__sum'] or 0
#     quizzes_taken = UserQuizAttempt.objects.filter(user=user).count()
#     user_rank = User.objects.filter(userquizattempt__score__gt=total_points).distinct().count() + 1

#     # Calculate user level (example: level up every 100 points)
#     user_level = total_points // 100 + 1

#     # Get recent activity
#     recent_attempts = UserQuizAttempt.objects.filter(user=user).order_by('-completed_at')[:5]

#     # Get available quizzes
#     topics = Topic.objects.all()
#     available_quizzes = Quiz.objects.filter(is_active=True).order_by('topic', 'difficulty')

#     context = {
#         'user': user,
#         'todays_quiz': todays_quiz,
#         'total_points': total_points,
#         'quizzes_taken': quizzes_taken,
#         'user_rank': user_rank,
#         'user_level': user_level,
#         'recent_attempts': recent_attempts,
#         'topics': topics,
#         'available_quizzes': available_quizzes,
#     }

#     return render(request, 'user_dashboard.html', context)
