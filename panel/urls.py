from django.conf.urls import patterns, url

urlpatterns = patterns('panel.views',
    url(r'^$', 'index', name='index'),

    url(r'^user/all/$', 'user_manage', name="user_manage"),
    url(r'^user/(?P<uid>\d+)/edit/$', 'user_edit', name="user_edit"),
    url(r'^user/all/data-ss/$', 'user_table_ss', name="user_table_ss"),

    url(r'^node/all/$', 'node_manage', name="node_manage"),
    url(r'^node/create/$', 'node_create', name="node_create"),
    url(r'^node/all/data-ss/$', 'node_table_ss', name="node_table_ss"),
    url(r'^node/(?P<node_id>\d+)/edit/$', 'node_edit', name="node_edit"),

    url(r'^topic/all/$', 'topic_manage', name="topic_manage"),
    #url(r'^topic/(?P<topic_id>\d+)/edit/$', 'topic_edit', name="topic_edit"),
    url(r'^topic/all/data-ss/$', 'topic_table_ss', name="topic_table_ss"),
    url(r'^topic/(?P<topic_id>\d+)/$', 'topic_edit', name="topic_edit"),

    url(r'^ajax/node/$', 'node_title_ajax', name="node_title_ajax"),
    url(r'^ajax/topic/bulk-delete/$', 'topic_bulk_delete', name="topic_bulk_delete"),
)
