from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginViews.as_view(), name='account login'),
    path('user/data/', views.UserInfo.as_view(), name='user info views'),
    path('check-session/', views.CheckSessionView.as_view(), name="auth session"),
    path('user/accounts/', views.UserAccountView.as_view(), name="user account view"),
]