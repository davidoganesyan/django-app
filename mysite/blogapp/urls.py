from django.urls import path
from .views import (ArticleListView)

app_name = "blogapp"

urlpatterns = [
    path("article/", ArticleListView.as_view(), name="articles_list"),
]
