
from django.contrib import admin
from django.urls import path, include
from authy_microservice.views.auth_views import *
from authy_microservice.views.service_views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/signup', SignupViewAPI.as_view()),
    path('auth/resend', ResendConfirmationAPI.as_view()),
    path('auth/confirm', ConfirmAccountAPI.as_view()),
    path('auth/signin', SignInViewAPI.as_view()),
    path('auth/refresh-token', RefreshTokenViewAPI.as_view()),
    path('auth/get-user', GetUserViewAPI.as_view()),
    path('auth/forgot-password', ForgetPasswordAPIView.as_view()),
    path('auth/set-password', SetPasswordAPIView.as_view()),
    path('auth/change-password', ChangePasswordAPIView.as_view()),
    path('auth/logout', LogoutAPIView.as_view()),
    path('auth/delete-user', DeleteUserAPIView.as_view()),

    path('books/', BookViewAPI.as_view()),

]
