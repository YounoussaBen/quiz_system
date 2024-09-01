from django.contrib import admin
from .models import User, Badge, Quiz

# Register your models here.

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(Quiz)