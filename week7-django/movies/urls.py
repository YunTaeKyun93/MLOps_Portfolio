from rest_framework import routers
from movies.views import MovieViewSet

router= routers.DefaultRouter()
router.register('movies', MovieViewSet)

urlpatterns = router.urls