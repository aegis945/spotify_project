from django.urls import path
from . import views

app_name = "playlist_tool"

urlpatterns = [
    path("", views.index, name="index"),
]