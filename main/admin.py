from django.contrib import admin

from main.models import Category, Post, Comment, Like

# Register your models here.
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
# admin.site.register(Like)
