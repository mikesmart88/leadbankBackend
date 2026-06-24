from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginViews.as_view(), name='account login'),
    path('user/data/', views.UserInfo.as_view(), name='user info views'),
    path('check-session/', views.CheckSessionView.as_view(), name="auth session"),
    path('user/accounts/', views.UserAccountView.as_view(), name="user account view"),
    path('transactions/', views.Transaction.as_view(), name="transactions views"),
    path('card/', views.CardView.as_view(), name="card views"),
    path('card/transactions/', views.CardTransactionView.as_view(), name="card transaction views"),
    path('account/verify/', views.VerificationView.as_view(), name="user veirification"),
    path('support/', views.SupportView.as_view(), name="companny support"),
    path('signup/', views.SignupViews.as_view(), name="create new user")
]