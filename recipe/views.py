from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework import filters, pagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from django.db import transaction
from django.db.models import Q, Count, OuterRef, Subquery
import logging
from . import models
from . import serializers
from users.permissions import role_based_permission, role_based_permission_class 
from users.models import User, UserProfile

logger = logging.getLogger(__name__)

class RecipeFilter(FilterSet):
    categories = CharFilter(method='filter_categories')
    search = CharFilter(method='filter_search')

    def filter_categories(self, queryset, name, value):
        logger.info(f"Filtering recipes by category IDs: {value}")
        if not value:
            return queryset
        try:
            category_ids = [int(cat_id.strip()) for cat_id in value.split(',') if cat_id.strip().isdigit()]
            if not category_ids:
                return queryset
            return queryset.filter(category__id__in=category_ids).distinct()
        except ValueError as e:
            logger.error(f"Invalid category IDs provided: {value}, error: {str(e)}")
            return queryset

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
    queryset = models.Recipe.objects.all().prefetch_related('comments')
    serializer_class = serializers.RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = RecipePagination
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'like', 'save']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by the authenticated user if 'my_recipes' query parameter is present
        if self.request.query_params.get('my_recipes') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        # Filter by saved recipes if 'saved_recipes' query parameter is present
        elif self.request.query_params.get('saved_recipes') == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(saved_by=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            logger.info(f"Queryset for list: {list(queryset)}")
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in RecipeViewSet list: {str(e)}", exc_info=True)
            return Response({"detail": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        logger.info(f"Create request data: {request.data}")
        logger.info(f"Authenticated user: {request.user if request.user.is_authenticated else 'Anonymous'}")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            logger.error("Unauthenticated user attempted to create a recipe")
            raise ValidationError("User must be authenticated to create a recipe")
        logger.info(f"Creating recipe for user: {self.request.user.email}")
        try:
            recipe = serializer.save(user=self.request.user)
            logger.info(f"Recipe {recipe.id} created successfully for user {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error creating recipe: {str(e)}")
            raise

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        logger.info(f"Retrieved recipe {instance.id} with comments: {list(instance.comments.all())}")
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = request.user
        if recipe.user != user and user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to update this recipe."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = request.user
        if recipe.user != user and user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to update this recipe."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = request.user
        if recipe.user != user and user.role != 'Admin':
            return Response(
                {"detail": "You do not have permission to delete this recipe."},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(recipe)
        logger.info(f"User {user.email} deleted recipe {recipe.id}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def most_liked(self, request):
        reaction_count = models.Reaction.objects.filter(
            recipe=OuterRef('pk')
        ).values('recipe').annotate(count=Count('id')).values('count')
        
        recipes = models.Recipe.objects.annotate(
            total_reactions=Subquery(reaction_count[:1])
        ).order_by('-total_reactions')[:5]
        
        serializer = self.get_serializer(recipes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        reaction_type = request.data.get('reaction_type', 'LIKE')

        if reaction_type not in ['LIKE', 'LOVE', 'WOW', 'SAD']:
            return Response(
                {"detail": "Invalid reaction type. Must be one of: LIKE, LOVE, WOW, SAD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reaction = models.Reaction.objects.filter(user=user, recipe=recipe).first()

        if reaction:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                logger.info(f"User {user.email} removed {reaction_type} reaction from recipe {recipe.id}")
                return Response({'status': 'reaction removed'})
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                logger.info(f"User {user.email} changed reaction to {reaction_type} for recipe {recipe.id}")
                return Response({'status': f'reaction updated to {reaction_type}'})
        else:
            models.Reaction.objects.create(user=user, recipe=recipe, reaction_type=reaction_type)
            logger.info(f"User {user.email} added {reaction_type} reaction to recipe {recipe.id}")
            return Response({'status': f'reaction added: {reaction_type}'})

    @action(detail=True, methods=['post'])
    def save(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if user in recipe.saved_by.all():
            recipe.saved_by.remove(user)
            logger.info(f"User {user.email} unsaved recipe {recipe.id}")
            return Response({
                'status': 'recipe unsaved',
                'is_saved_by_user': False,
                'saved_by_count': recipe.saved_by.count()
            })
        else:
            recipe.saved_by.add(user)
            logger.info(f"User {user.email} saved recipe {recipe.id}")
            return Response({
                'status': 'recipe saved',
                'is_saved_by_user': True,
                'saved_by_count': recipe.saved_by.count()
            })

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipe']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), role_based_permission(allowed_roles=['User', 'Chef', 'Admin'])]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['list', 'retrieve']:  # Explicitly set for GET requests
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        try:
            recipe_id = self.request.data.get('recipe')
            recipe = get_object_or_404(models.Recipe, id=recipe_id)
            existing_review = models.Review.objects.filter(reviewer=self.request.user, recipe=recipe).first()
            if existing_review:
                raise ValidationError("You have already reviewed this recipe. You can edit your existing review.")
            logger.info(f"Creating review for user: {self.request.user}")
            serializer.save(reviewer=self.request.user, recipe=recipe)
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}", exc_info=True)
            raise serializers.ValidationError(f"Failed to create review: {str(e)}")

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
        elif self.action in ['list', 'retrieve']:  
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        recipe_pk = self.kwargs.get('recipe_pk')
        if recipe_pk:
            return self.queryset.filter(recipe_id=recipe_pk)
        return self.queryset

    @transaction.atomic
    def perform_create(self, serializer):
        try:
            recipe_pk = self.kwargs.get('recipe_pk')
            logger.info(f"Creating comment for recipe {recipe_pk}, request data: {self.request.data}")
            if not recipe_pk:
                raise serializers.ValidationError("Recipe ID is required and must be provided in the URL.")
            recipe = get_object_or_404(models.Recipe, id=recipe_pk)
            comment = serializer.save(user=self.request.user, recipe=recipe)
            logger.info(f"Comment created: {comment.id} for recipe {recipe.id}")
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}", exc_info=True)
            raise serializers.ValidationError(f"Failed to create comment: {str(e)}")

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
    permission_classes = [IsAuthenticated, role_based_permission_class(allowed_roles=['Admin'])]
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
            logger.warning(f"User with email {email} not found")
            return Response(
                {"status": "failed", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error in RecipesByUserView for email {email}: {str(e)}", exc_info=True)
            return Response(
                {"status": "error", "message": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

