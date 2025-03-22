from rest_framework import serializers
from . import models
from users.serializers import UserProfileSerializer
from users.serializers import UserFullSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'name', 'slug']

class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = ['id', 'user', 'recipe', 'content', 'created', 'reaction_counts', 'user_reaction', 'can_delete']
        read_only_fields = ['user', 'recipe', 'created', 'reaction_counts', 'user_reaction', 'can_delete']

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty or whitespace.")
        return value

    def get_reaction_counts(self, obj):
        return obj.get_reaction_counts()

    def get_user_reaction(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            reaction = models.Reaction.objects.filter(comment=obj, user=user).first()
            return reaction.reaction_type if reaction else None
        return None

    def get_can_delete(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.can_delete(user)

class RecipeSerializer(serializers.ModelSerializer):
    user = UserFullSerializer(read_only=True)  # Changed to UserFullSerializer
    category = serializers.PrimaryKeyRelatedField(
        queryset=models.Category.objects.all(),
        many=True,
        write_only=True
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        source='category',
        many=True,
        read_only=True
    )
    category_names = serializers.StringRelatedField(
        source='category',
        many=True,
        read_only=True
    )
    saved_by = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reaction_counts = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_saved_by_user = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Recipe
        fields = [
            'id', 'title', 'ingredients', 'category', 'category_ids', 'category_names', 'user',
            'img', 'instructions', 'created_on', 'saved_by', 'reaction_counts', 'is_liked_by_user',
            'is_saved_by_user', 'comments'
        ]
        read_only_fields = [
            'user', 'created_on', 'saved_by', 'reaction_counts', 'is_liked_by_user',
            'is_saved_by_user', 'comments'
        ]

    def get_reaction_counts(self, obj):
        return obj.get_reaction_counts()

    def get_is_liked_by_user(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return models.Reaction.objects.filter(recipe=obj, user=user, reaction_type='LIKE').exists()
        return False

    def get_is_saved_by_user(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user in obj.saved_by.all()
        return False

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserProfileSerializer(read_only=True)

    class Meta:
        model = models.Review
        fields = ['id', 'reviewer', 'recipe', 'body', 'created', 'rating']
        read_only_fields = ['reviewer', 'created']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = models.Reaction
        fields = ['id', 'user', 'recipe', 'comment', 'reaction_type']
        read_only_fields = ['user']