from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import download_database
from contact_us.views import ContactUsAPIView
from django.conf import settings
from django.conf.urls.static import static



schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Recipe sharing website. Cook different recipe and make you daily life tasty!",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)



api_urlpatterns = [
    path("accounts/", include("users.urls")),
    path("recipes/", include("recipe.urls")),
    path('contact/', ContactUsAPIView.as_view(), name='contact-us'),
]

# v1_urlpatterns = [
#     path("", include("users.urls")),
#     path("", include("categories.urls")),
# ]

# v2_urlpatterns = [
#     path("users/", include("users.urls")),
#     path("categories/", include("categories.urls")),
# ]

# api_urlpatterns = [
#     path("v1/", include(v1_urlpatterns)),
# ]

urlpatterns = [
    path('', RedirectView.as_view(url='swagger/', permanent=True)),  # Redirect root URL to Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-ui'),
    path('admin/', admin.site.urls),
    path('db', download_database, name='download-database'),
    path("", include(api_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# urlpatterns = [
    
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-ui'),
#     path("admin/", admin.site.urls),
#     path("", include(api_urlpatterns)),
# ]



# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#     openapi.Info(
#         title="API Documentation",
#         default_version='v1',
#         description="Test description",
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

# urlpatterns = [
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-ui'),
#     # Your other URLs
# ]
