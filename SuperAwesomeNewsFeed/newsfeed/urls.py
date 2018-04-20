from django.urls import path
from . import views

app_name = 'newsfeed'

urlpatterns = [
    # localhost:8000/newsfeed/sources/
    path('sources/', views.list_sources, name='list_sources'),

    # localhost:8000/newsfeed/<str:all/favorites>
    path('<str:sort_by>/', views.newsfeed, name='newsfeed'),

    # localhost:8000/newsfeed/<news_id>/comments
    path('<int:news_id>/comments/', views.comments, name='comments'),

    # localhost:8000/newsfeed/comments/<comment_id>/
    path('comments/<int:comment_id>/', views.like_comment, name='like_comment'),

    # localhost:8000/newsfeed/favorite/<news_id>/
    path('favorite/<int:news_id>/', views.favorite, name='favorite'),

    # localhost:8000/newsfeed/sources/add_source/
    path('sources/add_source/', views.add_source, name='add_source'),

    # localhost:8000/newsfeed/sources/delete_source/<source_id>/
    path(r'sources/delete_source/<int:source_id>/', views.delete_source, name='delete_source'),
]