from django.urls import path
from . import views
from .views import MyTokenObtainPairView, RegisterView, PaidView,create_checkout, LogoutView, TestGet,create_payment

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView
)


urlpatterns = [
    path('getuser', views.UserView.as_view()),
    path('login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('blacklist', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('register', RegisterView.as_view()),
    path('logout', LogoutView.as_view()),
    path('paid', PaidView.as_view()),
    path('pay', create_checkout.as_view()),
    path('test', TestGet.as_view()),
    path('create-payment-intent', create_payment.as_view()),
    path('payment_successful', views.payment_successful.as_view()),
]