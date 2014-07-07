from django.db import models
from django.contrib.auth.models import User
import urllib
import hashlib


class profile(models.Model):
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=12, blank=True, null=True)
    use_gravatar = models.BooleanField(default=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def unread_mention(self):
        return self.user.received_mentions.filter(read=False)

    def old_mention(self):
        return self.user.received_mentions.filter(read=True)[0:5]

    def username(self):
        if self.nickname:
            return self.nickname
        else:
            return self.user.username

    def latest_activity(self):
        d = {}
        d['topic'] = self.user.topics.all().filter(deleted=False).order_by('-time_created')[0:10]
        d['post'] = self.user.posts.all().filter(deleted=False).order_by('-time_created')[0:10]
        return d

    def __unicode__(self):
        return self.user.username

    def avatar(self):
        da = ''  # default avatar
        dic = {}
        if self.use_gravatar:
            mail = self.user.email.lower()
            gravatar_url = "http://www.gravatar.com/avatar/"
            base_url = gravatar_url + hashlib.md5(mail).hexdigest() + "?"
            dic['small'] = base_url + urllib.urlencode({'d': da, 's': '40'})
            dic['middle'] = base_url + urllib.urlencode({'d': da, 's': '48'})
            dic['large'] = base_url + urllib.urlencode({'d': da, 's': '80'})
            return dic
        elif self.avatar_url:
            dic['small'] = self.avatar_url
            dic['middle'] = self.avatar_url
            dic['large'] = self.avatar_url
        return dic
        

class social(models.Model):
    user = models.OneToOneField(User)
    access_token = models.CharField(max_length=255)
    openid = models.CharField(max_length=255)
    avatar = models.URLField()
    
    def __unicode__(self):
        return self.user.username
    
