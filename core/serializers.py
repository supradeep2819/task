# core/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    def create(self, validated_data):
        # Ensure the role is valid ('member' or 'librarian')
        role = validated_data.get('role', User.Role.MEMBER.value)
        
        if role not in [User.Role.MEMBER.value, User.Role.LIBRARIAN.value]:
            raise ValueError("Role must be either 'member' or 'librarian'.")

        # Use create_user method to ensure password is hashed and validated
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],  # Automatically hashed by create_user
            role=role  # Set role after validation
        )
        return user

