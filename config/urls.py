from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls  import staticfiles_urlpatterns

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from parcelles.views import ParcelleViewSet
from transactions.views import TransactionViewSet
from messagerie.views import MessageViewSet


router = DefaultRouter()
router.register(r"parcelles", ParcelleViewSet, basename="parcelles")
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"messagerie", MessageViewSet, basename="messagerie")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

]
