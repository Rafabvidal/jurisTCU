from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Saida com os dados publicos do usuario logado."""

    name = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email']
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """Registro simplificado: o e-mail vira tambem o username."""

    name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': "O campo 'email' e obrigatorio.",
            'invalid': "Informe um e-mail valido.",
        },
    )
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este e-mail ja esta cadastrado.")
        return email

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        email = validated_data['email']
        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data.get('name', ''),
        )


class LoginSerializer(serializers.Serializer):
    """Login por e-mail e senha."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_email(self, value: str) -> str:
        return value.strip().lower()
