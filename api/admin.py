from django.contrib import admin
from .models import User, BlogPost,Like

# Register your models here.

@admin.register(User)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["id","name","email","date_of_birth","age"]

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["id","title","description","content","posted_on","posted_by","is_private"]

@admin.register(Like)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["id","post","user","comments"]
