from django.urls import path
from .views import hell_world_view, GroupsListView

app_name = "myapiapp"

urlpatterns = [
    path("hello/", hell_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
]
