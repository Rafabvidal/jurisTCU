"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from core.views import (
    AdminAuditLogView,
    AdminReindexView,
    LoginView,
    LogoutView,
    ProcessoViewset,
    RegisterView,
    SavedSearchViewSet,
    UserMeView,
)
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'processos', ProcessoViewset, basename='document')
router.register(r'saved-searches', SavedSearchViewSet, basename='saved-search')


auth_urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', UserMeView.as_view(), name='auth-me'),
]

admin_urlpatterns = [
    path('admin/audit-logs/', AdminAuditLogView.as_view(), name='admin-audit-logs'),
    path('admin/reindexar/', AdminReindexView.as_view(), name='admin-reindexar'),
]


def health(request):
    return HttpResponse('OK', content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(auth_urlpatterns)),
    path('api/', include(admin_urlpatterns)),
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('health/', health),
    path('silk/', include('silk.urls', namespace='silk')),
]
