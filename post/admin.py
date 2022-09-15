from django.contrib import admin

from .models import ReactionType, ReactionTweet, ReactionComment

admin.site.register(ReactionType)
admin.site.register(ReactionTweet)
admin.site.register(ReactionComment)

