from django.db import models
from django.contrib.auth.models import User
import markdown
import re
from django.core.urlresolvers import reverse
# Create your models here.


class topic(models.Model):
    user = models.ForeignKey(User, related_name='topics')
    title = models.CharField(max_length=160)
    content = models.TextField(blank=True, null=True)
    content_rendered = models.TextField(blank=True, null=True)
    click = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    node = models.ForeignKey('node', related_name='topics')
    time_created = models.DateTimeField(auto_now_add=True)
    last_replied = models.DateTimeField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            new = True
        else:
            new = False
        if not self.content:
            self.content = ''
        self.content_rendered = markdown.markdown(self.content, ['codehilite'],
                                                  safe_mode='escape')
        self.reply_count = self.post_set.all().count()
        to = []
        for u in re.findall(r'@(.*?)\s', self.content_rendered):
            try:
                user = User.objects.get(username=u)
            except:
                pass
            else:
                to.append(user)
                self.content_rendered = re.sub('@%s' % (u),
                                               '@<a href="%s" class="mention">%s</a>'
                                               % (reverse('user_info',
                                                          kwargs={'user_id': user.id}),
                                                  u),
                                               self.content_rendered)
        super(topic, self).save(*args, **kwargs)
        if to and new:
            for t in to:
                m = mention()
                m.sender = self.user
                m.receiver = t
                m.topic = self
                m.save()

        if new:
            self.last_replied = self.time_created
            self.save()


class node(models.Model):
    title = models.CharField(max_length=12)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title


class post(models.Model):
    user = models.ForeignKey(User, related_name='posts')
    topic = models.ForeignKey('topic')
    content = models.TextField()
    content_rendered = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.id) + self.topic.title

    def save(self, *args, **kwargs):
        if not self.id:
            new = True
        else:
            new = False
        if not self.content:
            self.content = ''
        self.content_rendered = markdown.markdown(self.content, ['codehilite'],
                                                  safe_mode='escape')
        to = []
        for u in re.findall(r'@(.*?)\s', self.content_rendered):
            try:
                user = User.objects.get(username=u)
            except:
                pass
            else:
                to.append(user)
                self.content_rendered = re.sub('@%s' % (u),
                                               '@<a href="%s" class="mention">%s</a>'
                                               % (reverse('user_info',
                                                          kwargs={'user_id': user.id}),
                                                  u),
                                               self.content_rendered)
        super(post, self).save(*args, **kwargs)
        if to and new:
            for t in to:
                m = mention()
                m.sender = self.user
                m.receiver = t
                m.post = self
                m.topic = self.topic
                m.save()
        if new:
            self.topic.last_replied = self.time_created
        self.topic.save()


class notification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications')
    receiver = models.ForeignKey(User, related_name='received_nofitications')
    topic = models.ForeignKey(topic, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=True)
    time_created = models.DateTimeField(auto_now_add=True)


class mention(models.Model):
    sender = models.ForeignKey(User, related_name='sent_mentions')
    receiver = models.ForeignKey(User, related_name='received_mentions')
    post = models.ForeignKey(post, blank=True, null=True)
    topic = models.ForeignKey(topic, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    read = models.BooleanField(default=False)
    time_created = models.DateTimeField(auto_now_add=True)


class appendix(models.Model):
    topic = models.ForeignKey(topic)
    time_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    content_rendered = models.TextField()

    def __unicode__(self):
        return self.topic.title + '-Appendix'

    def save(self, *args, **kwargs):
        if not self.content:
            self.content = ''
        self.content_rendered = markdown.markdown(self.content, ['codehilite'],
                                                  safe_mode='escape')
        super(appendix, self).save(*args, **kwargs)