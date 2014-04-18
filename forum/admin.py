from django.contrib import admin
from forum.models import topic, mention, notification, post, node
# Register your models here.


class post_inline(admin.StackedInline):
    model = post
    exclude = ['user', 'content_rendered']
    extra = 0


class topic_admin(admin.ModelAdmin):
    list_display = ('title', 'time_created', 'user', 'click', 'last_replied')
    list_filter = ('time_created',)
    search_fields = ['title', 'user__username']
    inlines = [post_inline]

admin.site.register(topic, topic_admin)
admin.site.register(node)
