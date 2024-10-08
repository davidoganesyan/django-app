from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (set_cookie_view, get_cookie_view, set_session_view, get_session_view, logout_view, AboutMeView,
                    RegisterView, FooBarView, ProfileUpdateView, UsersListView, UserDetailsView, HelloView)

app_name = "myauth"

urlpatterns = [
    # path("login/", login_view, name="login"),
    path("hello/", HelloView.as_view(), name="helo"),
    path("login/", LoginView.as_view(template_name="myauth/login.html", redirect_authenticated_user=True),
         name="login"),
    path("logout/", logout_view, name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("profile-update/<int:pk>/", ProfileUpdateView.as_view(), name="profile-update"),
    path("users-list/", UsersListView.as_view(), name="users-list"),
    path("user_details/<int:pk>/", UserDetailsView.as_view(), name="user-details"),
    path("register/", RegisterView.as_view(), name="register"),
    # path("logout/", MyLogoutView.as_view(), name="logout"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/set/", set_session_view, name="session-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
