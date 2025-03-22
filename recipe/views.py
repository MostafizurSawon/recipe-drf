from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework import filters, pagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from django.db.models import Q, Count, OuterRef, Subquery
import logging
from . import models
from . import serializers
# from users.permissions import role_based_permission  
from .permissions import role_based_permission
from users.models import User, UserProfile

logger = logging.getLogger(__name__)

class RecipeFilter(FilterSet):
    categories = CharFilter(method='filter_categories')
    search = CharFilter(method='filter_search')

    def filter_categories(self, queryset, name, value):
        logger.info(f"Filtering recipes by categories: {value}")
        if not value:
            return queryset
        category_names = [cat.strip() for cat in value.split(',')]
        query = Q()
        for cat_name in category_names:
            query |= Q(category__name__iexact=cat_name)
        return queryset.filter(query).distinct()

    def filter_search(self, queryset, name, value):
        logger.info(f"Searching recipes with query: {value}")
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) |
            Q(category__name__icontains=value)
        ).distinct()

class RecipePagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), role_based_permission(allowed_roles=['Admin'])]
        return [IsAuthenticatedOrReadOnly()]

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like', 'save']:
            return [IsAuthenticated()]  # Any authenticated user can perform these actions
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            logger.error("Unauthenticated user attempted to create a recipe")
            raise ValidationError("User must be authenticated to create a recipe")
        logger.info(f"Creating recipe for user: {self.request.user.email}")
        try:
            recipe = serializer.save(user=self.request.user)  # Save with User directly
            logger.info(f"Recipe {recipe.id} created successfully for user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error creating recipe: {str(e)}")
            raise

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def most_liked(self, request):
        reaction_count = models.Reaction.objects.filter(
            recipe=OuterRef('pk'),
            reaction_type='LIKE'
        ).values('recipe').annotate(count=Count('id')).values('count')
        recipes = models.Recipe.objects.annotate(
            like_count=Subquery(reaction_count[:1])
        ).order_by('-like_count')[:5]
        serializer = self.get_serializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        reaction = models.Reaction.objects.filter(user=user, recipe=recipe).first()
        if reaction and reaction.reaction_type == 'LIKE':
            reaction.delete()
            logger.info(f"User {user} unliked recipe {recipe.id}")
            return Response({'status': 'recipe unliked'})
        else:
            if reaction:
                reaction.delete()
            models.Reaction.objects.create(user=user, recipe=recipe, reaction_type='LIKE')
            logger.info(f"User {user} liked recipe {recipe.id}")
            return Response({'status': 'recipe liked'})

    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if user in recipe.saved_by.all():
            recipe.saved_by.remove(user)
            logger.info(f"User {user} unsaved recipe {recipe.id}")
            return Response({'status': 'recipe unsaved'})
        else:
            recipe.saved_by.add(user)
            logger.info(f"User {user} saved recipe {recipe.id}")
            return Response({'status': 'recipe saved'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), role_based_permission(allowed_roles=['User', 'Chef', 'Admin'])]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), role_based_permission(allowed_roles=['Admin'])]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        logger.info(f"Creating review for user: {self.request.user}")
        serializer.save(reviewer=self.request.user)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.reviewer != request.user and request.user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to update this review."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.reviewer != request.user and request.user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to delete this review."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipe']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), role_based_permission(allowed_roles=['User', 'Chef', 'Admin'])]
        elif self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        recipe_pk = self.kwargs.get('recipe_pk')
        if recipe_pk:
            return self.queryset.filter(recipe_id=recipe_pk)
        return self.queryset

    def perform_create(self, serializer):
        recipe_pk = self.kwargs.get('recipe_pk')
        logger.info(f"Creating comment for recipe {recipe_pk}, request data: {self.request.data}")
        if not recipe_pk:
            raise serializers.ValidationError("Recipe ID is required and must be provided in the URL.")
        recipe = get_object_or_404(models.Recipe, id=recipe_pk)
        serializer.save(user=self.request.user, recipe=recipe)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        user = request.user
        if not comment.can_delete(user):
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReactionViewSet(viewsets.ModelViewSet):
    queryset = models.Reaction.objects.all()
    serializer_class = serializers.ReactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipe', 'comment']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), role_based_permission(allowed_roles=['User', 'Chef', 'Admin'])]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), role_based_permission(allowed_roles=['Admin'])]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        logger.info(f"Creating reaction for user: {self.request.user}")
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        reaction = self.get_object()
        if reaction.user != request.user and request.user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to update this reaction."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        reaction = self.get_object()
        if reaction.user != request.user and request.user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to delete this reaction."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class RecipesByUserView(APIView):
    permission_classes = [IsAuthenticated, role_based_permission(allowed_roles=['Admin'])]
    pagination_class = RecipePagination

    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
            recipes = models.Recipe.objects.filter(user=user)
            
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(recipes, request)
            serializer = serializers.RecipeSerializer(page, many=True, context={'request': request})
            
            return paginator.get_paginated_response({
                "status": "success",
                "message": "Request Successful",
                "data": serializer.data,
            })
        except User.DoesNotExist:
            return Response(
                {"status": "failed", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )