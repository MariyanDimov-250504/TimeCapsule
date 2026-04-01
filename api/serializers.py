from rest_framework import serializers
from capsules.models import Capsule, CapsuleContent
from accounts.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'bio', 'profile_picture', 'date_joined']


class CapsuleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapsuleContent
        fields = ['id', 'content_type', 'title', 'text_content', 'image', 'created_at']


class CapsuleSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    contents = CapsuleContentSerializer(many=True, read_only=True)
    days_until_open = serializers.ReadOnlyField()
    is_openable = serializers.ReadOnlyField()

    class Meta:
        model = Capsule
        fields = [
            'id', 'title', 'description', 'creator', 'created_at', 'open_date',
            'privacy', 'status', 'cover_image', 'views_count', 'contents',
            'days_until_open', 'is_openable'
        ]
