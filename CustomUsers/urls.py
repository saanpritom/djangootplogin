from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from CustomUsers.views import UserAuthAPIView

urlpatterns = [
    # User token management views
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User Model Management views
    path('login/', UserAuthAPIView.as_view(), name='user-login-api-view'),
]
