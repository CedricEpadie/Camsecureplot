from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls  import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from parcelles.views import ParcelleViewSet,UserParcelleViewSet
from transactions.views import TransactionViewSet,UserTransactionViewSet,ParcelleHistoriqueViewSet
from messagerie.views import MessageViewSet


router = DefaultRouter()
router.register(r"parcelles", ParcelleViewSet, basename="parcelles")
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"user-transactions", UserTransactionViewSet, basename="user-transactions")
router.register(r"messagerie", MessageViewSet, basename="messagerie")
router.register(r"user-parcelles", UserParcelleViewSet, basename="user-parcelles")
router.register(r"parcelle-historique", ParcelleHistoriqueViewSet, basename="parcelle-historique")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

]
if settings.DEBUG:  # uniquement en développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)