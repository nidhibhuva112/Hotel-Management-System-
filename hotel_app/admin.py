from django.contrib import admin
from .models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'stars', 'created_at')  # use stars() method

admin.site.register(Feedback, FeedbackAdmin)


