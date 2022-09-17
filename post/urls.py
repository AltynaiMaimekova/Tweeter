from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tweet', views.TweetViewSet, basename='tweet')
# router.register('comment', views.CommentViewSet, basename='comment')


urlpatterns = [
    path('', include(router.urls)),
    path('tweet/<int:tweet_id>/comments/', views.CommentListCreateAPIView.as_view()),
    path('tweet/<int:tweet_id>/comments/<int:pk>/', views.CommentRetrieveUpdateDestroyAPIView.as_view()),
    path('tweet/<int:tweet_id>/<str:reaction_slug>/', views.PostTweetReaction.as_view()),
    path('tweet/<int:tweet_id>/comments/<int:comment_id>/<str:reaction_slug>/', views.PostCommentReaction.as_view()),
    path('recommendations/', views.RecommendationsView.as_view()),

]