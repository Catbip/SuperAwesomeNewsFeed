from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # localhost:8000/admin/
    path('admin/', admin.site.urls),

    # localhost:8000/
    path('', include('authentication.urls', namespace='authentication')),

    # localhost:8000/newsfeed/
    path('newsfeed/', include('newsfeed.urls', namespace='newsfeed')),
]
