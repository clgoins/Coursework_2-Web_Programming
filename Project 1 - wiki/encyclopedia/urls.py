from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entryName>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("newentry/", views.newEntry, name="newEntry"),
    path("edit/<str:entryName>", views.editEntry, name="editEntry"),
    path("random/", views.randomEntry, name="randomEntry")
]
