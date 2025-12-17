from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from projectile import env


swagger_info = openapi.Info(
    title=env.PROJECT_NAME,
    default_version=env.PROJECT_VERSION,
    description=env.PROJECT_DESCRIPTION,
    terms_of_service="https://www.google.com/policies/terms/",
    license=openapi.License(name="BSD License"),
)


schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('api/', include('user.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not env.PROD_ENV_DISABLE_SWAGGER:
    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]

if not env.PROD_ENV_DISABLE_ADMIN:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]
