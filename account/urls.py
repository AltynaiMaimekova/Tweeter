from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter


from . import views

router = DefaultRouter()
router.register('user_profile', views.UserProfileViewSet, basename='user_profile')

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    path('', include('rest_framework.urls')),
    path('token/', obtain_auth_token),
    path('', include(router.urls)),
    path('user_profile/<int:profile_id>/subscribe/', views.SubscribeView.as_view()),
]