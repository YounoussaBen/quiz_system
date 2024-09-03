from django.contrib import admin
from .models import User, Badge, Quiz, LearningMaterial

# Register your models here.

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(Quiz)
admin.site.register(LearningMaterial)