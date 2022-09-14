from django.db import models

from account.models import User


class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.__class__.__name__} from {self.user.username} at {self.updated}'

    @property
    def post_username(self):
        return self.user.username


class Tweet(Post):
    text = models.CharField(max_length=140)

    def get_likes(self):
        likes = LikeTweet.objects.filter(tweet=self, reaction=True)
        return likes.count()

    def get_dislikes(self):
        dislikes = LikeTweet.objects.filter(tweet=self, reaction=False)
        return dislikes.count()


class Comment(Post):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def get_likes(self):
        likes = LikeComment.objects.filter(comment=self, reaction=True)
        return likes.count()

    def get_dislikes(self):
        dislikes = LikeComment.objects.filter(comment=self, reaction=False)
        return dislikes.count()


class LikeTweet(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.BooleanField()

    class Meta:
        unique_together = ('user', 'tweet')

    def __str__(self):
        return f'like from {self.user}'


class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reaction = models.BooleanField()

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'like from {self.user}'





