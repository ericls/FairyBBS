from django.conf.urls import patterns, include, url

api_urlpatterns = patterns('forum.api',
    url(r'^topic/(?P<topic_id>\d+)/$', 'topic_api', name='topic_api'),
    url(r'^topics/$', 'topics_api', name='topics_api'),
    url(r'^post/(?P<post_id>\d+)/$', 'post_api', name='post_api'),
)

urlpatterns = patterns('forum.views',
    url(r'^$', 'index', name='index'),
    url(r'^topic/(?P<topic_id>\d+)/$', 'topic_view', name='topic_view'),
    url(r'^topic/(?P<topic_id>\d+)/reply/$', 'create_reply', name='create_reply'),
    url(r'^topic/(?P<topic_id>\d+)/append/$', 'add_appendix', name='add_appendix'),
    url(r'^post/(?P<post_id>\d+)/delete/$', 'del_reply', name="delete_post"),
    url(r'^previewer/$', 'previewer', name='previewer'),
    url(r'node/(?P<node_id>\d+)/$', 'node_view', name='node_view'),
    url(r'^node/(?P<node_id>\d+)/create/$', 'create_topic', name='create_topic'),
    url(r'^search/(?P<keyword>.*?)/$', 'search', name='search'),
    url(r'^recent/$', 'recent', name='recent'),
    #url(r'^(?P<key>.*?)/$', 'to', name='goto'),
)
