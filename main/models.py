from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.email
    
    def increase_score(self, points):
        self.total_score += points
        new_level = (self.total_score // 100) + 1
        if new_level > self.level:
            self.level = new_level
            self.award_level_badge()
        self.save()

    def award_level_badge(self):
        level_badges = LevelBadge.objects.filter(level=self.level)
        for level_badge in level_badges:
            UserBadge.objects.get_or_create(user=self, badge=level_badge.badge)


# Topic Model
class Topic(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Quiz Model
class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Normal', 'Normal'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='EASY')  # Choices: Easy, Normal, Hard, etc.
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quizzes')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(default=timezone.timedelta(minutes=30))  
    required_level = models.IntegerField(default=1) 

    def __str__(self):
        return self.title

# Question Model
class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        # Add other types if necessary
    ]
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='MCQ')
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.text

# Option Model
class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

# UserQuizAttempt Model
class UserQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Completed', 'Completed'), ('In Progress', 'In Progress')])

# UserAnswer Model
class UserAnswer(models.Model):
    attempt = models.ForeignKey(UserQuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)

# Badge Model
class Badge(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to='badges/')

    def __str__(self):
        return self.name

class LevelBadge(models.Model):
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    level = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.badge.name} - Level {self.level}"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.email} - {self.badge.name}"
    
@receiver(post_save, sender=User)
def award_default_badge(sender, instance, created, **kwargs):
    if created:
        default_badge = LevelBadge.objects.get(level=0).badge
        UserBadge.objects.create(user=instance, badge=default_badge)

class LearningMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='learning_materials')
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES, default='OTHER')
    file = models.FileField(upload_to='learning_materials/files/', null=True, blank=True)  # Allows any type of file
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title