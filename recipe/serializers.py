from rest_framework import serializers
from .models import Recipe, Comment, Category, Reaction, Review
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'firstName', 'lastName', 'role']
        ref_name = 'RecipeUserSerializer'  # Added unique ref_name

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'recipe', 'user', 'content', 'created', 'can_delete']
        read_only_fields = ['recipe', 'user', 'created', 'can_delete']

    def get_can_delete(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_delete(request.user)
        return False

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'user', 'recipe', 'comment', 'reaction_type']

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    rating_display = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'recipe', 'body', 'created', 'rating', 'rating_display']

    def get_rating_display(self, obj):
        return obj.get_star_display()

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class RecipeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), source='category', write_only=True
    )
    category_names = serializers.SlugRelatedField(
        many=True, read_only=True, source='category', slug_field='name'
    )
    reaction_counts = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_saved_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'ingredients', 'instructions', 'created_on', 'category',
            'category_ids', 'category_names', 'img', 'user', 'comments',
            'reaction_counts', 'user_reaction', 'is_liked_by_user', 'is_saved_by_user'
        ]
        read_only_fields = ['user', 'comments', 'created_on', 'category', 'category_names', 'reaction_counts', 'is_liked_by_user', 'is_saved_by_user']

    def get_reaction_counts(self, obj):
        return obj.get_reaction_counts()

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = Reaction.objects.filter(user=request.user, recipe=obj).first()
            return reaction.reaction_type if reaction else None
        return None

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Reaction.objects.filter(user=request.user, recipe=obj, reaction_type='LIKE').exists()
        return False

    def get_is_saved_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(id=request.user.id).exists()
        return False