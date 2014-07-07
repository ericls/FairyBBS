# -*- coding: utf-8 -*-
from django.template import RequestContext
from forum.models import node, topic
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
import json
from django.db.models import Q
# Create your views here.


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def index(request):
    return render_to_response('panel/index.html', {'title': _('home')})


@user_passes_test(lambda u: u.is_superuser)
def user_manage(request):
    return render_to_response('panel/user-manage.html', {'title': _('user management')})


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def user_table_data(request):
    data = {}
    data['aaData'] = []
    for u in User.objects.all():
        info_list = [u.username,u.email]
        data['aaData'].append(info_list)
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def user_table_ss(request):
    fields = ['id','username', 'email']
    order_dir = request.GET.get('sSortDir_0')
    order_field = int(request.GET.get('iSortCol_0'))
    if order_dir == 'asc':
        order_by = '%s' % fields[order_field]
    else:
        order_by = '-%s' % fields[order_field]
    length = int(request.GET.get('iDisplayLength',10))
    key = request.GET.get('sSearch')
    start = int(request.GET.get('iDisplayStart',0))
    if key:
        if key.isdigit():
            condition = Q(email__contains=key)|Q(username__contains=key)|Q(id=key)
        else:
            condition = Q(email__contains=key)|Q(username__contains=key)
        users = User.objects.filter(condition).order_by(order_by)
    else:
        users = User.objects.all().order_by(order_by)
    data = {}
    data['aaData'] = []
    data['iTotalDisplayRecords'] = len(users)
    users = users[start:start+length]
    data['iTotalRecords'] = User.objects.count()
    for u in users:
        info_list = [u.id, u.username, u.email]
        info_list.append('<a href="%s" class="label label-success">%s</a>' % \
                (
                    reverse('panel:user_edit', kwargs={'uid': u.id}),
                _('edit')
                )
            )
        data['aaData'].append(info_list)
    return HttpResponse(json.dumps(data))



@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def user_edit(request,uid):
    u = User.objects.get(id=uid)
    if request.method == 'GET':
        return render_to_response('panel/user-edit.html',{'title': _('edit user'), 'user': u},
               context_instance=RequestContext(request))
    elif request.method == 'POST':
        data = request.POST
        username = data['username']
        email = data.get('email', False)
        password = data.get('password', False)
        active = data.has_key('active')
        admin = data.has_key('admin')
        nickname = data.get('nickname')
        location = data.get('location')
        website = data.get('website')
        use_gravatar = data.has_key('gravatar')
        u.username = username
        u.email = email
        if password:
            u.set_password(password)
        u.is_active = active
        u.is_superuser = admin
        u.save()
        p = u.profile
        p.nickname = nickname
        p.website = website
        p.location = location
        p.use_gravatar = use_gravatar
        p.save()
        return HttpResponseRedirect(reverse('panel:user_edit', args=[uid]))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def node_manage(request):
    return render_to_response('panel/node-manage.html', {'title': _('node management')})


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def node_table_ss(request):
    fields = ['id','title']
    order_dir = request.GET.get('sSortDir_0')
    order_field = int(request.GET.get('iSortCol_0'))
    if order_dir == 'asc':
        order_by = '%s' % fields[order_field]
    else:
        order_by = '-%s' % fields[order_field]
    length = int(request.GET.get('iDisplayLength',10))
    key = request.GET.get('sSearch')
    start = int(request.GET.get('iDisplayStart',0))
    if key:
        if key.isdigit():
            condition = Q(title__contains=key)|Q(id=key)
        else:
            condition = Q(title__contains=key)
        nodes = node.objects.filter(condition).order_by(order_by)
    else:
        nodes = node.objects.all().order_by(order_by)
    data = {}
    data['aaData'] = []
    data['iTotalDisplayRecords'] = len(nodes)
    nodes = nodes[start:start+length]
    data['iTotalRecords'] = node.objects.count()
    for n in nodes:
        info_list = [n.id, n.title]
        info_list.append('<a href="%s" class="label label-success">%s</a>' %\
                (
                    reverse('panel:node_edit', kwargs={'node_id': n.id}),
                    _('edit')
                )
            )
        data['aaData'].append(info_list)
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def node_edit(request,node_id):
    n = node.objects.get(id=node_id)
    if request.method == 'GET':
        return render_to_response('panel/node-edit.html', {'title': _('edit node'), 'node': n},
               context_instance=RequestContext(request))
    elif request.method == 'POST':
        data = request.POST
        title = data.get('title', 'empty')
        description = data.get('description', None)
        n.title = title
        n.description = description
        n.save()
        return HttpResponseRedirect(reverse('panel:node_edit', args=[n.id]))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def node_create(request):
    if request.method == 'GET':
        return render_to_response('panel/node-create.html', {'title': _('create node')},
               context_instance=RequestContext(request))
    elif request.method == 'POST':
        n = node()
        data = request.POST
        title = data.get('title', 'empty')
        description = data.get('description', None)
        n.title = title
        n.description = description
        n.save()
        return HttpResponseRedirect(reverse('panel:node_manage'))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def topic_manage(request):
    return render_to_response('panel/topic-manage.html', {'title': _('topic management')})


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))


def topic_edit(request,topic_id):
    t = topic.objects.get(id=topic_id)
    if request.method == 'GET':
        return render_to_response('panel/topic-edit.html',{'title': _('edit topic'), 'topic': t},
               context_instance=RequestContext(request))
    elif request.method == 'POST':
        data = request.POST
        title = data['title']
        node_title = data['node']
        content = data['content']
        order = data['order']
        n = node.objects.get(title=node_title)
        t.title = title
        t.node = n
        t.content = content
        t.order = order
        t.save()
        return HttpResponseRedirect(reverse('panel:topic_edit', args=[t.id]))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def topic_table_ss(request):
    fields = ['id', 'title', 'user__username', 'node__title']
    order_dir = request.GET.get('sSortDir_0')
    order_field = int(request.GET.get('iSortCol_0'))
    if order_dir == 'asc':
        order_by = '%s' % fields[order_field]
    else:
        order_by = '-%s' % fields[order_field]
    length = int(request.GET.get('iDisplayLength',10))
    key = request.GET.get('sSearch')
    start = int(request.GET.get('iDisplayStart',0))
    if key:
        if key.isdigit():
            condition = Q(title__contains=key)|Q(node__title__contains=key)|Q(user__username__contains=key)|Q(id=key)
        else:
            condition = Q(title__contains=key)|Q(node__title__contains=key)|Q(user__username__contains=key)
        topics = topic.objects.filter(condition, deleted=False).order_by(order_by)
    else:
        topics = topic.objects.filter(deleted=False).order_by(order_by)
    data = {}
    data['aaData'] = []
    data['iTotalDisplayRecords'] = len(topics)
    topics = topics[start:start+length]
    data['iTotalRecords'] = topic.objects.count()
    for t in topics:
        info_list = [t.id, t.title, t.user.username, t.node.title]
        info_list.append('<a href="%s" class="label label-success">%s</a>' % \
                (
                    reverse('panel:topic_edit', kwargs={'topic_id': t.id}),
                    _('edit')
                )
            )
        data['aaData'].append(info_list)
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def node_title_ajax(request):
    key = request.GET.get('query')
    condition = Q(title__contains=key)
    nodes = node.objects.filter(condition)
    data = {}
    data['suggestions'] = []
    for n in nodes.all():
        data['suggestions'].append(n.title)
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: u.is_superuser, login_url=reverse('signin'))
def topic_bulk_delete(request):
    ids = request.GET['ids']
    ids = ids.split(',')
    ts = []
    for i in ids:
        t = topic.objects.get(id=i)
        t.deleted = True
        t.save()
        ts.append(t)
    return HttpResponse(ts)
