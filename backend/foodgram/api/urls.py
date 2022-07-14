from django.urls import include, path
from rest_framework import routers

from . import views

router_v1 = routers.DefaultRouter()


router_v1.register(
    r'tags',
    views.TagViewSet,
    basename='tags',
)

router_v1.register(
    r'ingredients',
    views.IngredientViewSet,
    basename='ingredients',
)

router_v1.register(
    r'users',
    views.CustomUserViewSet,
    basename='users',
)
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     views.CommentViewSet,
#     'comments'
# )

app_name = 'api'

urlpatterns = [
    path(
        '',
        include(router_v1.urls)
    ),
    path('auth/', include('djoser.urls.authtoken'))
]
