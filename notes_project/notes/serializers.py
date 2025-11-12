from rest_framework import serializers
from .models import Note, NoteVersion
from django.contrib.auth import get_user_model

User = get_user_model()

class NoteVersionSerializer(serializers.ModelSerializer):
    editor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NoteVersion
        fields = ['id', 'note', 'title', 'content', 'editor', 'created_at', 'version']
        read_only_fields = ['id', 'note', 'editor', 'created_at', 'version']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class NoteSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    collaborators = serializers.PrimaryKeyRelatedField(many=True,queryset=User.objects.all(),required=False)

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content',
            'owner', 'collaborators',
            'last_updated', 'version'
        ]
        read_only_fields = ['id', 'owner', 'last_updated', 'version']

class NoteUpdateSerializer(serializers.ModelSerializer):
    last_known_version = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Note
        fields = ['title', 'content', 'last_known_version']
