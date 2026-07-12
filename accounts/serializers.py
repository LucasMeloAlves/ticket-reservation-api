from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# Come mostro un utente in risposta (senza la password, ovviamente).
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone_number", "date_joined"]
        read_only_fields = ["id", "role", "date_joined"]


# Serializer per la registrazione di un nuovo utente.
class RegisterSerializer(serializers.ModelSerializer):
    # La password si puo' solo scrivere (write_only) e viene controllata
    # dalle regole di sicurezza di Django.
    password = serializers.CharField(write_only=True, validators=[validate_password])
    # In fase di registrazione puoi scegliere solo USER o ORGANIZER.
    # Gli admin si creano a parte (createsuperuser / seed).
    role = serializers.ChoiceField(
        choices=["USER", "ORGANIZER"],
        default="USER",
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone_number"]
        read_only_fields = ["id"]

    # Non permetto due utenti con lo stesso username.
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Questo username e' gia' in uso.")
        return value

    # Creo l'utente cifrando la password (non la salvo mai in chiaro).
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Serializer del login: oltre ai token, aggiungo il ruolo dentro il token
# e restituisco anche i dati dell'utente.
class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
