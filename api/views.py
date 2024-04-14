from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, Like, User, NonBuiltInUserToken
from .serializers import BlogPostSerializer, UserSerializer, LikeSerializer
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from .authentication import UserTokenAuthentication
import datetime
from rest_framework.permissions import IsAuthenticated


class UserView(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get(self, request, pk=None):
        if pk is not None:
            user_obj = User.objects.get(pk=pk)
            serializer1 = UserSerializer(instance=user_obj)
            serializer2 = UserSerializer(request.user)
            print("serializer 1 : ",serializer1.data)
            print("serializer 2 : ",serializer2.data)
            if serializer1.data == serializer2.data:
                return Response({"data": serializer1.data})
            else :
                return Response({'msg':"You Cann't access any others user data"},status=status.HTTP_400_BAD_REQUEST)   
        else:
            data = User.objects.all().values()
            serializer = UserSerializer(instance=data, many=True)

        return Response({"data": serializer.data})

    def put(self, request, pk=None):
            user_obj = User.objects.get(pk=pk)
            serializer1 = UserSerializer(instance=user_obj)
            serializer2 = UserSerializer(request.user)
            print("serializer 1 : ",serializer1.data)
            print("serializer 2 : ",serializer2.data)
            if serializer1.data == serializer2.data: 
                serializer = UserSerializer(data=request.data, instance=user_obj, partial=True)
            else : 
                 return Response({'msg':"You Cann't access any others user data"},status=status.HTTP_400_BAD_REQUEST)   
                 
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"Message": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST
                )
    def delete(self, request, pk=None):
            user_obj = User.objects.get(pk=pk)
            serializer1 = UserSerializer(instance=user_obj)
            serializer2 = UserSerializer(request.user)
            print("serializer 1 : ",serializer1.data)
            print("serializer 2 : ",serializer2.data)
            if serializer1.data == serializer2.data: 
                user_obj.delete()
                return Response({"Message": "User deleted"},status=status.HTTP_200_OK)
            else:
                 return Response({'msg':"You Cann't access any others user data"},status=status.HTTP_400_BAD_REQUEST)
        
    
class UserRegisterView(APIView):
    def post(self, request):
        name = request.data.get("name", None)
        age = request.data.get("age",None)
        date_of_birth = request.data.get("date_of_birth",None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if user := User.objects.filter(email=email).exists():
            return Response({"Message": "User with the email already exists"})
        else:
            hashed_password = make_password(password)
            print("hashed_password : ",hashed_password)
            user_obj = User.objects.create(email=email, password=hashed_password,name=name,age=age,date_of_birth=date_of_birth)
            user_obj.save()
            return Response({"Message": "User Successfully created"})


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if user := User.objects.filter(email=email).first():
            user = auth.authenticate(username=email, password=password)
            if user is not None:
                token = NonBuiltInUserToken.objects.create(user_id=user.id)
                return Response(
                    {"Token": str(token), "is_superuser": user.is_superuser},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response({"Message": "Invalid username or password"})
        else:
            return Response({"Message": "Incorrect credentials"})


class PostListAPIView(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get(self, request, *args, **kwargs):
        posts = BlogPost.objects.all()
        print("data.is_private : ",posts)
        serializer = BlogPostSerializer(instance=posts, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = BlogPostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            post.posted_by = request.user
            post.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get(self, request, pk, *args, **kwargs):
        print(request.user)
        post = BlogPost.objects.get(pk=pk)
        print("post : ",post.posted_by)
        if post.is_private:
            if request.user == post.posted_by:
                serializer = BlogPostSerializer(post)
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            else :
                return Response({"error": "Private Post"}, status=status.HTTP_400_BAD_REQUEST)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = BlogPostSerializer(post)
        likes_serializer = LikeSerializer(post.like_set.all(), many=True)
        return Response({"data": serializer.data,"likes": likes_serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        post = BlogPost.objects.get(pk=pk)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        data = request.data
        serializer = BlogPostSerializer(post, data=data, partial=True)
        if serializer.is_valid():
            if request.user == post.posted_by:
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response(
                {"error": "You are not authorized to edit this post"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        post = BlogPost.objects.get(pk=pk)
        if post is None:
            return Response(
                {"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if request.user == post.posted_by:
            post.delete()
            return Response({"Message": "Object deleted!"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "You are not authorized to delete this post"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LikeListApiView(APIView):
    # def post(self, request, *args, **kwargs):
    #         data = request.data
    #         serializer = LikeSerializer(data=data)
    #         if serializer.is_valid():
    #             post = serializer.save()
    #             print("post : ",post)
    #             print("post user : ",post.user)
    #             post.user = request.user
    #             post.save()
    #             return Response({"message":"Like the blog!","data": serializer.data}, status=status.HTTP_201_CREATED)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def delete(self, request, post_id):
    #         post = get_object_or_404(BlogPost, pk=post_id)
    #         like = get_object_or_404(Like, user=request.user, post=post)
    #         like.delete()
    #         return Response({"Message": "Unlike the blog!"},status=status.HTTP_204_NO_CONTENT)
    
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def post(self, request, pk):
        # Check if the blog post exists
        blog_post = get_object_or_404(BlogPost, pk=pk)

        # Check if the user has already liked the blog post
        like_exists = Like.objects.filter(post=blog_post, user=request.user).exists()
        if like_exists:
            return Response({"detail": "You have already liked this blog post"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new like for the blog post
        like = Like.objects.create(post=blog_post, user=request.user)
        return Response({"detail": "Blog post liked successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        # Check if the blog post exists
        blog_post = get_object_or_404(BlogPost, pk=pk)

        # Check if the user has liked the blog post
        like = Like.objects.filter(post=blog_post, user=request.user).first()
        if not like:
            return Response({"detail": "You have not liked this blog post"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete the like
        like.delete()
        return Response({"detail": "Blog post unliked successfully"}, status=status.HTTP_204_NO_CONTENT)
    

class MeUser(APIView):
    authentication_classes = [
        UserTokenAuthentication,
    ]

    def get(self,request,format=None):
            serilizer = UserSerializer(request.user)
            return Response({"data":serilizer.data},status=status.HTTP_200_OK)