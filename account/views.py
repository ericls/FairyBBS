#encoding=utf-8
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from fairy import conf
from forum.models import topic, post, node
from django.contrib import auth
import json
import markdown
from django.contrib.auth import login, authenticate, logout
from account.models import profile, social
from forum.views import error
import urllib, urllib2, re, random
from django.core.validators import RegexValidator
import tempfile
import shutil
import os
from django.core.files.storage import FileSystemStorage
# Create your views here.

storage = FileSystemStorage(
    location=conf.UPLOAD_PATH,
    base_url='/static/upload/'
)

alphanumeric = RegexValidator(r'^[0-9a-zA-Z\_]*$', 'Only alphanumeric characters and underscore are allowed.')


def user_info(request, user_id):
    try:
        u = User.objects.get(id=user_id)

        return render_to_response('user-info.html', {'request': request, 'title': u'用户信息',
                                                     'user': u, 'conf': conf,
                                                     'topics': u.profile.latest_activity()['topic'],
                                                     'post_list_title': u'用户%s的最新主题' % (u.profile.username())})
    except:
        return error(request, '用户没有填写详细信息')


def reg(request):
    if request.method == 'GET':
        return render_to_response('reg.html', {'conf': conf, 'title': u'注册'},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        try:
            alphanumeric(username)
        except:
            return error(request, '用户名只允许英文字母、数字及下划线"_"(QQ登陆用户不受此限制)')

        #todo 检测邮箱是否重复
        try:
            User.objects.get(username=username)
        except:
            pass
        else:
            return error(request, '用户已存在')

        #todo 密码强度测试
        if password != password2 or password == '' or password2 == '':
            return error(request, '两次输入的密码不一致或者为空')

        user = User.objects.create_user(username, email, password)
        user = authenticate(username=username, password=password)
        login(request, user)
        p = profile()
        p.user = user
        p.save()
        return HttpResponseRedirect(reverse('index'))


def user_login(request):
    if request.method == 'GET':
        return render_to_response('login.html', {'conf': conf, 'title': u'登陆'},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None:
            return error(request, '登陆失败，请检查用户名密码是否错误')
        login(request, user)
        return HttpResponseRedirect(reverse('index'))


def setting(request):
    if request.method == 'GET':
        return render_to_response('user-setting.html', {'request': request,
                                                        'conf': conf,
                                                        'title': u'设置'},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        request.user.profile.website = request.POST['website']
        request.user.email = request.POST['email']
        request.user.profile.save()
        request.user.save()
        return render_to_response('user-setting.html', {'request': request,
                                                        'conf': conf,
                                                        'title': u'设置'},
                                  context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def view_mention(request):
    old = request.user.profile.old_mention()
    new = request.user.profile.unread_mention()
    for m in new:
        m.read = True
        m.save()
    return render_to_response('user-mention.html', {'request': request, 'title': u'查看提醒',
                                                    'conf': conf,
                                                    'new': new,
                                                    'old': old, },
                              context_instance=RequestContext(request))


def change_password(request):
    u = request.user
    if request.method == 'GET':
        return render_to_response('change-password.html', {'request': request, 'title': u'修改密码',
                                                           'conf': conf},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        old = request.POST['old-password']
        new = request.POST['password']
        if request.POST['password'] != request.POST['password2'] or request.POST['password'] == '' or request.POST['password2'] == '':
            return error(request, '两次输入的密码不一致或者为空')
        if authenticate(username=u.username, password=old):
            u.set_password(new)
            u.save()
            return error(request, u'密码修改成功', reverse('index'))
        else:
            return error(request, u'填写错误，可能是原始密码错误或', reverse('change_password'))


def user_avatar(request):
    u = request.user
    if request.method == 'GET':
        return render_to_response('user-avatar.html', {'request': request, 'title': u'头像设置',
                                                       'conf': conf},
                                  context_instance=RequestContext(request))
    else:
        use_gravatar = request.POST.getlist('gravatar') == ['true']
        request.user.profile.use_gravatar = use_gravatar
        f = request.FILES.get('file', None)
        if f:
            extension = os.path.splitext(f.name)[-1]
            if f.size > 524288:
                return error(request, u'文件太大')
            if (extension not in ['.jpg', '.png', '.gif']) or ('image' not in f.content_type):
                return error(request, u'类型不允许')
            name = storage.save(storage.get_available_name(str(request.user.id) + extension), f)
            url = storage.url(name)
            request.user.profile.avatar_url = url
        request.user.profile.save()
        return HttpResponseRedirect(reverse('user_avatar'))


###############
#oauth related#
###############
def GenerateUsername(nickname):
    i = 0
    MAX = 999
    while (i < MAX):
        username = nickname + '__qq__' + str(random.randint(0, MAX))
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
    raise Exception('All random username are taken')


def qq_oauth(request):
    if request.method == 'GET':
        if (not request.GET['code']) or (request.GET['state'] != 'pythoncclogin'):
            return error(request, '请求错误')
        code = request.GET['code']
        url = 'https://graph.qq.com/oauth2.0/token'
        data = {'grant_type': 'authorization_code',
                'client_id': '',
                'client_secret': '',
                'code': code,
                'redirect_uri': ''}
        req = urllib2.Request(url, urllib.urlencode(data))
        res = urllib2.urlopen(req)
        try:
            access_token = re.findall(r'access_token=(.*?)&', res.read())[0]
        except:
            return error(request, u'抱歉，未从腾讯获取到有效的授权信息，可能是和腾讯通信失败，请重试\n')
        url_openid = 'https://graph.qq.com/oauth2.0/me'
        data_openid = {'access_token': access_token}
        req_openid = urllib2.Request(url_openid, urllib.urlencode(data_openid))
        res_openid = urllib2.urlopen(req_openid)
        try:
            JSON_openid = json.loads(res_openid.read()[10:-3])
        except:
            return error(request, u'抱歉，未从腾讯获取到有效的授权信息，可能是和腾讯通信失败，请重试')
        openid = JSON_openid['openid']
        try:
            u = social.objects.get(openid=openid).user
        except:
            url_info = 'https://graph.qq.com/user/get_user_info'
            data_info = {'oauth_consumer_key': '',
                         'access_token': access_token,
                         'openid': openid}
            req_info = urllib2.Request(url_info, urllib.urlencode(data_info))
            res_info = urllib2.urlopen(req_info)
            JSON_info = json.loads(res_info.read())
            username = JSON_info['nickname']
            nickname = username
            if JSON_info['figureurl_qq_2']:
                avatar = JSON_info['figureurl_qq_2']
            else:
                avatar = JSON_info['figureurl_2']
            password = User.objects.make_random_password()
            try:
                u = User.objects.get(username=username)
            except:
                pass
            else:
                username = GenerateUsername(nickname)
            u = User(username=username)
            u.set_password(password)
            u.save()
            p = profile(user=u,
                        #avatar=avatar,
                        nickname=nickname,
                        avatar_url=avatar,
                        use_gravatar=False)
            p.save()
            s = social(user=u,
                       access_token=access_token,
                       openid=openid,
                       avatar=avatar, )
            s.save()
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index')) #login succeed
        else:
            u.social.access_token = access_token
            u.social.save()
            u.backend = 'django.contrib.auth.backends.ModelBackend'
            if u is not None and u.is_active:
                auth.login(request, u)
                return HttpResponseRedirect(reverse('index')) #login succeed
            else:
                return error(request, u'授权失败，请重试')