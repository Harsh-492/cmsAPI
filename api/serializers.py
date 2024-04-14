from rest_framework import serializers
from .models import BlogPost, User, Like


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = (
            "id",
            "title",
            "description",
            "content",
            "is_private",
            "posted_on",
            "posted_by",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    class Meta:
        model = BlogPost
        fields = '_all_'  # Include all fields for now

    def get_likes(self):
        likes_count = Like.objects.filter(post=obj).count()
        return likes_count
    

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'  # Include all fields for now
