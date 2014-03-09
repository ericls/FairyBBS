from django.contrib import admin
from forum.models import topic, mention, notification, post, node
# Register your models here.


class topic_admin(admin.ModelAdmin):
    list_display = ('title', 'time_created', 'user', 'click', 'last_replied')
    list_filter = ('time_created',)
    #readonly_fields = ('user',)
    search_fields = ['title', 'user']

admin.site.register(topic, topic_admin)
admin.site.register(post)
admin.site.register(node)
