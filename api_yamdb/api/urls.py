from django.urls import include, path
from rest_framework import routers

from . views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    get_jwt_user,
    signup_confirmation_code
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', signup_confirmation_code, name='signup'),
    path('v1/auth/token/', get_jwt_user, name='token')
]
