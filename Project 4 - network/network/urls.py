
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:userProfile>", views.profile, name="profile"),
    path("following", views.following, name='following'),

    # API request paths
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("like", views.like, name="like"),
    path("likeCount", views.getLikeCount, name="likeCount"),
    path("post", views.post, name="post")
]
