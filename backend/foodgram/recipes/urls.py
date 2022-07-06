from django.urls import include, path
# from rest_framework import routers

from . import views

# router_v1 = routers.DefaultRouter()

# router_v1.register(
#     r'users',
#     views.UserViewSet,
#     basename='users',
# )
# 
# router_v1.register(
#     r'categories',
#     views.CategoryViewSet,
#     basename='categories',
# )
# 
# router_v1.register(
#     r'genres',
#     views.GenreViewSet,
#     basename='genres',
# )
# 
# router_v1.register(
#     r'titles',
#     views.TitleViewSet,
#     basename='titles',
# )
# 
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     views.ReviewViewSet,
#     'reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     views.CommentViewSet,
#     'comments'
# )
# router_v1.register(
#     r'users',
#     views.UserViewSet,
#     basename='users'
# )
# router_v1.register(
#     r'auth/signup',
#     views.UserCreationViewSet,
#     basename='user_creation'
# )

app_name = 'recipes'

urlpatterns = [
    # path(
    #     'v1/',
    #     include(router_v1.urls)
    # ),
    # path(
    #     'v1/auth/token/',
    #     views.CustomTokenObtainView.as_view(),
    #     name='get_token'
    # ),
]
