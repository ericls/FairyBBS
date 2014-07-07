# -*- coding: utf-8 -*-
from account.models import profile
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.context_processors import csrf
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from fairy import conf
from forum.models import topic, post, node, appendix
import json
import markdown
import operator
# Create your views here.


def error(request, msg, back=None):
    return render_to_response('error.html', {'conf': conf, 'title': _('notice'),
                                             'msg': msg,
                                             'back': back,
                                             'request': request, })


def previewer(request):
    c = request.REQUEST['content']
    md = {}
    md['marked'] = markdown.markdown(c, ['codehilite'], safe_mode='escape')
    return HttpResponse(json.dumps(md))


def index(request):
    conf.nodes = node.objects.all()
    conf.user_count = profile.objects.count()
    conf.topic_count = topic.objects.count()
    conf.post_count = post.objects.count()
    topics = topic.objects.all().filter(deleted=False).order_by('-last_replied')[0:30]
    post_list_title = _('latest topics')
    return render_to_response('forum/index.html', {'topics': topics, 'title': _('home'),
                                             'request': request,
                                             'post_list_title': post_list_title,
                                             'conf': conf})


def topic_view(request, topic_id):
    t = topic.objects.get(id=topic_id)
    t.click += 1
    t.save()
    n = t.node
    posts = t.post_set.filter(deleted=False)
    try:
        page = request.GET['page']
    except:
        page = None
    if page == '1':
        page = None
    return render_to_response('forum/topic.html', {'conf': conf, 'title': t.title,
                                             'request': request,
                                             'topic': t,
                                             'node': n,
                                             'pager': page,
                                             'posts': posts
    },
                              context_instance=RequestContext(request))


def create_reply(request, topic_id):
    if request.method == 'POST':
        t = topic.objects.get(id=topic_id)
        r = post()
        r.topic = t
        if request.POST['content']:
            r.content = request.POST['content']
        else:
            messages.add_message(request, messages.WARNING, _('content cannot be empty'))
            return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id':topic_id}))
        r.user = request.user
        r.save()
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t.id}))
    elif request.method == 'GET':
        return error(request, 'don\'t get')


def node_view(request, node_id):
    try:
        page = request.GET['page']
    except:
        page = None
    if page == '1':
        page = None
    n = node.objects.get(id=node_id)
    topics = topic.objects.filter(node=n,deleted=False)
    return render_to_response('forum/node-view.html', {'request': request, 'title': n.title,
                                                 'conf': conf,
                                                 'topics': topics,
                                                 'node': n,
                                                 'node_view': True,
                                                 'pager': page,})


def create_topic(request, node_id):
    n = node.objects.get(id=node_id)
    if request.method == 'GET':
        return render_to_response('forum/create-topic.html', {'node': n, 'title': _('create topic'),
                                                        'request': request,
                                                        'conf': conf},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        t = topic()
        t.content = request.POST.get('content') or ''
        t.node = n
        t.title = request.POST['title']
        if not t.title:
            messages.add_message(request, messages.WARNING, _('title cannot be empty'))
            return HttpResponseRedirect(reverse('create_topic', kwargs={'node_id':node_id}))
        if not request.user.is_authenticated():
            return error(request, '请登陆', reverse('signin'))
        t.user = request.user
        t.save()
        return HttpResponseRedirect(reverse('topic_view',
                                            kwargs={'topic_id': t.id}))


def search(request, keyword):
    keys = keyword.split(' ')
    condition = reduce(operator.and_,
                       (Q(title__contains=x) for x in keys))
    topics = topic.objects.filter(condition)
    try:
        page = request.GET['page']
    except:
        page = None
    if page == '1':
        page = None
    return render_to_response('forum/index.html', {'request': request, 'title': _('%s-search result') % (keyword),
                                             'conf': conf, 'pager': page,
                                             'topics': topics,
                                             'post_list_title': _('search %s') % (keyword), })


def recent(request):
    try:
        page = request.GET['page']
    except:
        page = None
    if page == '1':
        page = None
    topics = topic.objects.all().filter(deleted=False)
    return render_to_response('forum/index.html', {'request': request, 'title': _('latest topics'),
                                             'conf': conf,
                                             'topics': topics,
                                             'recent': 'reccent',
                                             'pager': page,
                                             'post_list_title': _('latest posted topics'), })


@staff_member_required
def del_reply(request, post_id):
    p = post.objects.get(id=post_id)
    t_id = p.topic.id
    p.deleted = True
    p.save()
    p.topic.save()
    return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t_id}))


def del_topic(request, topic_id):
    t = topic.objects.get(id=topic_id)
    if request.user != t.user and (not request.user.is_superuser):
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t.id}))
    n_id = t.node.id
    t.deleted = True
    t.save()
    return HttpResponseRedirect(reverse('node_view', kwargs={'node_id': n_id}))


def edit_topic(request, topic_id):
    t = topic.objects.get(id=topic_id)
    if request.user != t.user and (not request.user.is_superuser):
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t.id}))
    if request.method == 'GET':
        return render_to_response('forum/edit-topic.html',{'request': request, 'conf': conf,
                                                     'topic': t,
                                                     'title': _('topic edit')},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        t.title = request.POST['title']
        t.content = request.POST['content']
        if not t.title:
            messages.add_message(request, messages.WARNING, _('title cannot be empty'))
            return HttpResponseRedirect(reverse('edit_topic', kwargs={'topic_id': t.id}))
        t.save()
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t.id}))
    

def add_appendix(request, topic_id):
    t = topic.objects.get(id=topic_id)
    n = t.node
    if request.user != t.user:
        return error(request, _('you cannot add appendix to other people\'s topic' ))
    if request.method == 'GET':
        return render_to_response('forum/append.html', {'request': request, 'title': _('add appendix'),
                                                  'node': n, 'conf': conf,
                                                  'topic': t, },
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        a = appendix()
        a.content = request.POST['content']
        if not a.content:
            messages.add_message(request, messages.WARNING, _('content cannot be empty'))
            return HttpResponseRedirect(reverse('add_appendix', kwargs={'topic_id': t.id}))
        a.topic = t
        a.save()
        return HttpResponseRedirect(reverse('topic_view', kwargs={'topic_id': t.id}))


def node_all(request):
    nodes = {}
    nodes[u'分类1'] = list(node.objects.filter(id__in=[1]).all())
    return render_to_response('forum/node-all.html', {'request': request, 'title': _('all nodes'),
                                                'conf': conf,
                                                'nodes': nodes, })
