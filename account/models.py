from django.db import models

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscription = models.ManyToManyField('UserProfile', through='Subscription', related_name='followed_by')

    def __str__(self):
        return self.user.username


class Subscription(models.Model):
    followed = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='followed')
    follower = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='follower')
    start_following = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('followed', 'follower')

    def save(self, *args, **kwargs):
        if self.followed != self.follower:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.follower} followed {self.followed} at {self.start_following}'



