from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import Quiz, User, UserQuizAttempt, Topic, UserBadge, UserAnswer, Question, Option
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import TopicForm, QuizForm, QuestionForm, OptionFormSet
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
import json
from .forms import UserUpdateForm, CustomPasswordChangeForm

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
                return redirect('user_home')
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
            return redirect('user_home')
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
def admin_profile(request, user_id):
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

@login_required
def user_home(request):
    user = request.user
    completed_quizzes = UserQuizAttempt.objects.filter(user=user, status='Completed').count()
    completed_attempts = UserQuizAttempt.objects.filter(user=user, status='Completed')
    completed_quizzes_ids = completed_attempts.values_list('quiz__id', flat=True)
    badges = UserBadge.objects.filter(user=user)
    
    # Get Quiz of the Day
    today = timezone.now().date()
    quiz_of_the_day = Quiz.objects.filter(is_active=True, created_at__date=today).first()
    if not quiz_of_the_day:
        quiz_of_the_day = Quiz.objects.filter(is_active=True).order_by('-created_at').first()
    
    # Get popular quizzes
    popular_quizzes = Quiz.objects.filter(is_active=True).order_by('-attempts').distinct()[:6]
    total_score = user.total_score
    progress = total_score % 100

    context = {
        'user': user,
        'completed_quizzes': completed_quizzes,
        'badges': badges,
        'quiz_of_the_day': quiz_of_the_day,
        'popular_quizzes': popular_quizzes,
        'progress': progress,
        'completed_quizzes_ids': completed_quizzes_ids,
    }
    return render(request, 'user/user_home.html', context)

@login_required
def quizzes(request):
    user = request.user
    
    # Fetch all topics
    topics = Topic.objects.all()
    
    # Fetch quizzes by topic and difficulty, and check if the user has already taken them
    quizzes_by_topic = []
    for topic in topics:
        quizzes = Quiz.objects.filter(topic=topic, is_active=True)
        topic_quizzes = []
        
        for quiz in quizzes:
            # Check if the user has already attempted this quiz
            user_attempt = UserQuizAttempt.objects.filter(user=user, quiz=quiz, status='Completed').exists()
            
            topic_quizzes.append({
                'quiz': quiz,
                'is_taken': user_attempt,
            })

        quizzes_by_topic.append({
            'topic': topic,
            'quizzes': topic_quizzes,
        })

    context = {
        'user': user,
        'quizzes_by_topic': quizzes_by_topic,
    }
    return render(request, 'user/quizzes.html', context)

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    user = request.user
    
    # Check if the user meets the level requirement
    if user.level < quiz.required_level:
        messages.error(request, f"You need to be at least level {quiz.required_level} to start this quiz.")
        return redirect('user_home')
    
    # Check if the user has already completed this quiz
    completed_attempt = UserQuizAttempt.objects.filter(user=user, quiz=quiz, status='Completed').first()
    if completed_attempt:
        messages.info(request, "You have already completed this quiz.")
        return redirect('user_home')
    
    # Check if the user has an in-progress attempt
    existing_attempt = UserQuizAttempt.objects.filter(user=user, quiz=quiz, status='In Progress').first()
    if existing_attempt:
        return redirect('take_quiz', attempt_id=existing_attempt.id)
    
    # Create a new attempt
    attempt = UserQuizAttempt.objects.create(user=user, quiz=quiz, status='In Progress')
    return redirect('take_quiz', attempt_id=attempt.id)

@login_required
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(UserQuizAttempt, id=attempt_id, user=request.user)
    quiz = attempt.quiz
    user = request.user
    
    if attempt.status == 'Completed':
        messages.info(request, "This quiz attempt has already been completed.")
        return redirect('user_home')
    
    questions = list(quiz.questions.all())
    answered_questions = set(UserAnswer.objects.filter(attempt=attempt).values_list('question_id', flat=True))
    
    if request.method == 'POST':
        data = json.loads(request.body)
        question_id = data.get('question_id')
        selected_option_id = data.get('selected_option_id')
        
        if question_id in answered_questions:
            return JsonResponse({'error': 'This question has already been answered.'}, status=400)
        
        question = get_object_or_404(Question, id=question_id, quiz=quiz)
        selected_option = get_object_or_404(Option, id=selected_option_id, question=question)
        
        is_correct = selected_option.is_correct
        points_earned = question.points if is_correct else 0
        
        UserAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )
        
        attempt.score += points_earned
        attempt.save()
        
        old_level = user.level
        user.increase_score(points_earned)
        new_level = user.level
        level_up = new_level > old_level
        
        if len(answered_questions) + 1 == len(questions):
            attempt.status = 'Completed'
            attempt.save()
        
        return JsonResponse({
            'is_correct': is_correct,
            'points_earned': points_earned,
            'total_score': attempt.score,
            'quiz_completed': attempt.status == 'Completed',
            'level_up': level_up,
            'new_level': new_level
        })
    
    unanswered_questions = [q for q in questions if q.id not in answered_questions]
    
    return render(request, 'user/take_quiz.html', {
        'quiz': quiz,
        'questions': json.dumps([{
            'id': q.id,
            'text': q.text,
            'points': q.points,
            'options': [{
                'id': o.id,
                'text': o.text
            } for o in q.options.all()]
        } for q in unanswered_questions]),
        'attempt': attempt,
        'total_questions': len(questions),
        'answered_questions': len(answered_questions),
        'user_level': user.level,
        'user_score': user.total_score
    })

@login_required
def continue_quiz(request, attempt_id):
    return redirect('take_quiz', attempt_id=attempt_id)


@login_required
def leaderboard_view(request):
    users = User.objects.order_by('-level', '-total_score')
    paginator = Paginator(users, 20)  # Show 20 users per page
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_data = []
        for user in page:
            latest_badge = UserBadge.objects.filter(user=user).order_by('-earned_at').first()
            user_data.append({
                'full_name': user.get_full_name(),
                'email': user.email,
                'level': user.level,
                'total_score': user.total_score,
                'profile_picture': user.profile_picture.url if user.profile_picture else None,
                'latest_badge': {
                    'name': latest_badge.badge.name,
                    'icon': latest_badge.badge.icon.url
                } if latest_badge else None
            })
        return JsonResponse({
            'users': user_data,
            'has_next': page.has_next()
        })

    context = {
        'page': page,
        'user': request.user,
        'user_badges': UserBadge.objects.filter(user=request.user).select_related('badge')
    }
    return render(request, 'user/leaderboard.html', context)


@login_required
def my_profile(request):
    user = request.user
    user_form = UserUpdateForm(instance=user)
    password_form = CustomPasswordChangeForm(user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('my_profile')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated successfully.')
                return redirect('my_profile')

    # Get the user's ranking
    user_ranking = User.objects.filter(
        Q(level__gt=user.level) | 
        Q(level=user.level, total_score__gt=user.total_score) |
        Q(level=user.level, total_score=user.total_score, id__lt=user.id)
    ).count() + 1

    total_users = User.objects.filter(is_active=True).count()
    
    # Get user badges
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')

    # Calculate progress to next level
    points_to_next_level = (user.level + 1) * 100 - user.total_score
    progress_percentage = (user.total_score % 100) if user.total_score > 0 else 0

    context = {
        'user': user,
        'user_form': user_form,
        'password_form': password_form,
        'user_ranking': user_ranking,
        'total_users': total_users,
        'user_badges': user_badges,
        'points_to_next_level': points_to_next_level,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'user/my_profile.html', context)

@login_required
def update_profile_picture(request):
    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']
            request.user.save()
            return JsonResponse({'success': True, 'new_picture_url': request.user.profile_picture.url})
        elif 'remove_picture' in request.POST:
            request.user.profile_picture = None
            request.user.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})