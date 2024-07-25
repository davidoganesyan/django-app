from django.urls import path
from .views import (ArticleListView, ArticleDetailView, LatestArticlesFeed)

app_name = "blogapp"

urlpatterns = [
    path("article/", ArticleListView.as_view(), name="articles_list"),
    path("article/<int:pk>", ArticleDetailView.as_view(), name="article"),
    path("article/latest/feed/", LatestArticlesFeed(), name="articles-feed"),
]
