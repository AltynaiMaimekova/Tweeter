from django.db import IntegrityError
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404

from .models import Tweet, Comment, ReactionTweet, ReactionComment, ReactionType
from account.models import Subscription
from .serializers import TweetSerializer, CommentSerializer
from .permissions import IsAuthorPermission
from .paginations import StandardPagination


class TweetViewSet(ModelViewSet):
    serializer_class = TweetSerializer
    queryset = Tweet.objects.all()
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.query_params.get('user')
        if user:
            queryset = queryset.filter(user__username=user)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(text__icontains=search)
        return queryset


class CommentListCreateAPIView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]
    pagination_class = StandardPagination

    def get_queryset(self):
        # print(self.kwargs)
        return self.queryset.filter(tweet_id=self.kwargs['tweet_id'])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            tweet=get_object_or_404(Tweet, id=self.kwargs['tweet_id'])
        )


class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthorPermission, ]


# Reactions
class PostTweetReaction(APIView):
    def get(self, request, tweet_id, reaction_slug):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        user_reaction = get_object_or_404(ReactionType, slug=reaction_slug)
        try:
            reaction = ReactionTweet.objects.create(user=request.user, tweet=tweet, reaction=user_reaction)
        except IntegrityError:
            reaction = ReactionTweet.objects.get(user=request.user, tweet=tweet)
            if reaction.reaction == user_reaction:
                reaction.reaction = None
                # reaction.save()
                # reaction.delete()
                data = {'delete': f'tweet {tweet_id} lost reaction from {request.user.username}'}
            else:
                reaction.reaction = user_reaction
                # reaction.save()
                data = {'message': f'tweet {tweet_id} got {reaction.reaction.slug} from {request.user.username}'}
            reaction.save()
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f'tweet {tweet_id} got {reaction.reaction.slug} from {request.user.username}'}
            return Response(data, status=status.HTTP_201_CREATED)


class PostCommentReaction(APIView):
    def get(self, request, tweet_id, comment_id, reaction_slug):
        comment = get_object_or_404(Comment, id=comment_id)
        user_reaction = get_object_or_404(ReactionType, slug=reaction_slug)
        try:
            reaction = ReactionComment.objects.create(user=request.user, comment=comment, reaction=user_reaction)
        except IntegrityError:
            reaction = ReactionComment.objects.get(user=request.user, comment=comment)
            if reaction.reaction.slug == user_reaction.slug:
                reaction.delete()
                data = {'delete': f'comment {comment_id} to tweet {tweet_id} lost {reaction.reaction.slug} from {request.user.username}'}
            else:
                reaction.reaction = user_reaction
                reaction.save()
                data = {'message': f'comment {comment_id} to tweet {tweet_id} got {reaction.reaction.slug} from {request.user.username}'}
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {'message': f'comment {comment_id} to tweet {tweet_id} got {reaction.reaction.slug} from {request.user.username}'}
            return Response(data, status=status.HTTP_201_CREATED)


class RecommendationsView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        subscriptions = Subscription.objects.filter(follower=request.user.profile)
        recommendations = []
        for s in subscriptions:
            tweets = Tweet.objects.filter(user=s.followed.user)
            for t in tweets:
                recommendations.append(t)
        recommendations.sort(key=lambda x: x.created, reverse=True)
        data = {'message': f'recommended tweets {recommendations}'}
        return Response(data, status=status.HTTP_200_OK)

## Код ниже - это первоначальная реализация лайков и дизлайков (Задание 5)

# class PostTweetLike(APIView):
#     def get(self, request, tweet_id):
#         tweet = get_object_or_404(Tweet, id=tweet_id)
#         try:
#             like = LikeTweet.objects.create(user=request.user, tweet=tweet, reaction=True)
#         except IntegrityError:
#             like = LikeTweet.objects.get(user=request.user, tweet=tweet)
#             if like.reaction:
#                 like.delete()
#                 data = {'delete': f'tweet {tweet_id} lost like from {request.user.username}'}
#             else:
#                 like.delete()
#                 like = LikeTweet.objects.create(user=request.user, tweet=tweet, reaction=True)
#                 data = {'message': f'tweet {tweet_id} got like from {request.user.username}'}
#             return Response(data, status=status.HTTP_200_OK)
#         else:
#             data = {'message': f'tweet {tweet_id} got like from {request.user.username}'}
#             return Response(data, status=status.HTTP_201_CREATED)
#
#
# class PostTweetDislike(APIView):
#     def get(self, request, tweet_id):
#         tweet = get_object_or_404(Tweet, id=tweet_id)
#         try:
#             dislike = LikeTweet.objects.create(user=request.user, tweet=tweet, reaction=False)
#         except IntegrityError:
#             like = LikeTweet.objects.get(user=request.user, tweet=tweet)
#             if like.reaction:
#                 like.delete()
#                 dislike = LikeTweet.objects.create(user=request.user, tweet=tweet, reaction=False)
#                 data = {'delete': f'tweet {tweet_id} got dislike from {request.user.username}'}
#             else:
#                 like.delete()
#                 data = {'delete': f'tweet {tweet_id} lost dislike from {request.user.username}'}
#             return Response(data, status=status.HTTP_200_OK)
#         else:
#             data = {'message': f'tweet {tweet_id} got dislike from {request.user.username}'}
#             return Response(data, status=status.HTTP_201_CREATED)
#
#
# class PostCommentLike(APIView):
#     def get(self, request, tweet_id, comment_id):
#         comment = get_object_or_404(Comment, id=comment_id)
#         try:
#             like = LikeComment.objects.create(user=request.user, comment=comment, reaction=True)
#         except IntegrityError:
#             like = LikeComment.objects.get(user=request.user, comment=comment)
#             if like.reaction:
#                 like.delete()
#                 data = {'delete': f'comment {comment_id} lost like from {request.user.username}'}
#             else:
#                 like.delete()
#                 like = LikeComment.objects.create(user=request.user, comment=comment, reaction=True)
#                 data = {'message': f'comment {comment_id} got like from {request.user.username}'}
#             return Response(data, status=status.HTTP_200_OK)
#         else:
#             data = {'message': f'comment {comment_id} got like from {request.user.username}'}
#             return Response(data, status=status.HTTP_201_CREATED)
#
#
# class PostCommentDislike(APIView):
#     def get(self, request, tweet_id, comment_id):
#         comment = get_object_or_404(Comment, id=comment_id)
#         try:
#             dislike = LikeComment.objects.create(user=request.user, comment=comment, reaction=False)
#         except IntegrityError:
#             like = LikeComment.objects.get(user=request.user, comment=comment)
#             if like.reaction:
#                 like.delete()
#                 dislike = LikeComment.objects.create(user=request.user, comment=comment, reaction=False)
#                 data = {'delete': f'comment {comment_id} got dislike from {request.user.username}'}
#             else:
#                 like.delete()
#                 data = {'delete': f'comment {comment_id} lost dislike from {request.user.username}'}
#             return Response(data, status=status.HTTP_200_OK)
#         else:
#             data = {'message': f'tweet {comment_id} got dislike from {request.user.username}'}
#             return Response(data, status=status.HTTP_201_CREATED)