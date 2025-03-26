from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RecipeViewSet,
    CategoryViewSet,
    ReviewViewSet,
    CommentViewSet,
    ReactionViewSet,
    RecipesByUserView  
)

router = DefaultRouter()
router.register('lists', RecipeViewSet, basename='recipe')
router.register('categories', CategoryViewSet, basename='category')
router.register('reviews', ReviewViewSet, basename='review')
router.register('comments', CommentViewSet, basename='comment')
router.register('reactions', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('', include(router.urls)),
    path('lists/<int:pk>/like/', RecipeViewSet.as_view({'post': 'like'}), name='recipe-like'),
    path('lists/<int:pk>/save/', RecipeViewSet.as_view({'post': 'save'}), name='recipe-save'),
    path('lists/<int:recipe_pk>/comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='recipe-comments'),
    path('lists/<int:recipe_pk>/comments/<int:pk>/', CommentViewSet.as_view({'delete': 'destroy'}), name='comment-destroy'),
    path('by-user/<str:email>/', RecipesByUserView.as_view(), name='recipes_by_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)