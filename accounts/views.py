from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    RoleTokenObtainPairSerializer,
    UserSerializer,
)

User = get_user_model()


# POST /api/auth/register/
# Crea un nuovo utente e gli restituisce subito i token per essere loggato.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # controlla i dati
        user = serializer.save()
        # Genero i token JWT (access = per usare l'API, refresh = per rinnovarlo).
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=201,
        )


# POST /api/auth/login/
# Login: dai username e password, ricevi i token JWT.
class LoginView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer


# GET /api/auth/me/
# Restituisce i dati dell'utente attualmente loggato.
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
