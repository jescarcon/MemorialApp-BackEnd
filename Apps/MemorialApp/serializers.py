from rest_framework import serializers
from .models import Note, Medium
from .models import User

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id',
                  'title', 
                  'description',
                  'add_date',
                  'image',
                  'medium'
                ]
        
class MediumSerializer(serializers.ModelSerializer):
    generate_ai_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Medium
        fields = ['id',
                  'title', 
                  'description',
                  'add_date',
                  'image',
                  'rating', 
                  'status', 
                  'category',
                  'user',
                  'begin_date',
                  'finish_date',
                  'generate_ai_image'
                ]

    def create(self, validated_data):
        validated_data.pop('generate_ai_image', None)
        return super().create(validated_data)
    
#- USUARIO CUSTOM MEMORIAL -
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'avatar', 'two_factor_enabled','two_fa_code','two_fa_expiration']
        extra_kwargs = {
            'password': {'write_only': True},
            'two_fa_code': {'read_only': True},  
            'two_fa_expiration': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # Cifra la contraseña
        else:
            raise serializers.ValidationError({"password": "La contraseña es obligatoria al crear un usuario."})
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        if password:
            instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

##