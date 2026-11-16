from rest_framework.routers import DefaultRouter
from .views import AparelhoViewSet, ClienteViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("aparelhos", AparelhoViewSet, basename="aparelho")
urlpatterns = router.urls
