from django.contrib import admin
from django.urls import path
from .views import (
    PostListAPIView,
    PostDetailAPIView,
    UserLoginView,
    UserView,
    UserRegisterView,
    LikeListApiView,
    MeUser
    
)

urlpatterns = [
    path("accounts/", UserRegisterView.as_view()),
    path("accounts/login/", UserLoginView.as_view()),
    path("accounts/<int:pk>/",  UserView.as_view()),
    path('me/',MeUser.as_view()),
    path("blog/", PostListAPIView.as_view()),
    path("blog/<int:pk>/", PostDetailAPIView.as_view()),
    path("like/<int:pk>/", LikeListApiView.as_view()),
    # path("users/<int:pk>/", UserView.as_view()),
]
