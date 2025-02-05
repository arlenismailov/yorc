from django.urls import path, include
from .views import *
from knox import views as knox_views

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('confirm-email/<int:token>/', ConfirmEmailAPIView.as_view(), name='confirm-email'),
    path('confirm-email/<int:token>/', ConfirmEmailAPIView.as_view(), name='confirm-email'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
 