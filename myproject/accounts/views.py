from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.mail import send_mail
from django.urls import reverse
from .serializers import RegisterSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.views import LoginView as KnoxLoginView
from .serializers import RegisterSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import VerifyResetCodeSerializer


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Генерируем ссылку для подтверждения
            token = user.id  # Простой токен (для примера)
            confirm_url = request.build_absolute_uri(
                reverse('confirm-email', args=[token])
            )
            send_mail(
                'Подтверждение регистрации',
                f'Перейдите по ссылке для подтверждения: {confirm_url}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Пользователь зарегистрирован. Проверьте почту для подтверждения.'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailAPIView(APIView):
    def get(self, request, token):
        try:
            user = User.objects.get(id=token)
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response({'message': 'Email успешно подтвержден!'}, status=status.HTTP_200_OK)
            return Response({'message': 'Email уже подтвержден.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'Неверный токен.'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(KnoxLoginView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, format=None):
        # Проверяем введенные данные
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем аутентифицированного пользователя
        user = serializer.validated_data['user']
        if not user.is_active:
            return Response({"error": "Ваш аккаунт не подтвержден. Проверьте почту."}, status=status.HTTP_400_BAD_REQUEST)

        # Устанавливаем пользователя и возвращаем токен
        self.request.user = user
        return super().post(request, format=format)

