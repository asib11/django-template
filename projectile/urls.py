from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from projectile import env


def custom_page_not_found_view(request, exception=None, *args, **kwargs):
    target_url = getattr(env, 'FRONTEND_404_URL', 'https://vn4et.com/404') or 'https://vn4et.com/404'
    return redirect(target_url)


handler404 = 'projectile.urls.custom_page_not_found_view'


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
    path('api/v1/', include('user.urls')),
    path('api/v1/', include('contact.urls')),
    path('api/v1/', include('program.urls')),
    path('api/v1/', include('payment.urls')),
    path('api/v1/', include('assessment.urls')),
    path('api/v1/', include('booking.urls')),
    path('api/v1/', include('callchat.urls')),
    path('api/v1/', include('talent_portal.urls')),
    path('api/v1/', include('notification.urls')),
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
    
if not env.DEBUG:
    urlpatterns += [
        re_path(r'^.*$', custom_page_not_found_view, name='not-found-redirect'),
    ]
