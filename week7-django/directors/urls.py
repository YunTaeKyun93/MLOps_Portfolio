from rest_framework import routers
from directors.views import DirectorViewSet

router = routers.DefaultRouter()
router.register('directors', DirectorViewSet)


urlpatterns = router.urls