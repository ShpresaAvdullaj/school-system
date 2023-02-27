from django.urls import path
from users.views import registration_view, LogoutView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path("register/", registration_view, name="register"),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

]
"""
The blacklist app also provides a management command, flushexpiredtokens,
which will delete any tokens from the outstanding list and blacklist that 
have expired. You should set up a cron job on your server or hosting 
platform which runs this command daily.
"""
