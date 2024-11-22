from django.shortcuts import render

def index(request):
    return render(request, "playlist_tool/index.html")