from django.contrib import admin
from .models import User, Badge, LevelBadge, UserBadge
# Register your models here.

admin.site.register(User)
admin.site.register(Badge)
admin.site.register(LevelBadge)
admin.site.register(UserBadge)
