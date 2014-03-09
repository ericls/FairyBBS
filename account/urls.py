from django.conf.urls import patterns, include, url

urlpatterns = patterns('account.views',
    url(r'^(?P<user_id>\d+)/info/$', 'user_info', name='user_info'),
    url(r'^reg/$', 'reg', name='reg'),
    url(r'^signin/$', 'user_login', name='signin'),
    url(r'^setting/$', 'setting', name='user_setting'),
    url(r'^signout/$', 'user_logout', name='signout'),
    url(r'^mention/$', 'view_mention', name='mention'),
    url(r'^oauth/qq/$', 'qq_oauth', name='qq_oauth'),
    url(r'password/$', 'change_password', name='change_password'),
    url(r'avatar/$', 'user_avatar', name='user_avatar'),
    #url(r'^(?P<key>.*?)/$', 'to', name='goto'),
)
