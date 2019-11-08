from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from CustomUsers.views import (UserAuthAPIView, UserFCMKeyView,
                               UserOTPVerificationView, UserDetailBasicCreateView,
                               UserIsAgreedUpdateView)

urlpatterns = [
    # User token management views
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User Model Management views
    path('login/', UserAuthAPIView.as_view(), name='user-login-api-view'),
    path('fcm/key/<slug:pk>/', UserFCMKeyView.as_view(), name='user-fcm-api-view'),
    path('otp/verify/<slug:pk>/', UserOTPVerificationView.as_view(), name='otp-verification-view'),
    path('detail/create/', UserDetailBasicCreateView.as_view(), name='user-detail-basic-create-view'),
    path('detail/agreed/', UserIsAgreedUpdateView.as_view(), name='user-is-agreed-accept-view'),
]
