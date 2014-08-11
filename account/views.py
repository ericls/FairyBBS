#encoding=utf-8
from PIL import Image
from account.models import profile, social
from django.contrib import auth
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.core.context_processors import csrf
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
#from django.utils.translation import LANGUAGE_SESSION_KEY
from fairy import conf
from forum.models import topic, post, node
from forum.views import error
import json
import markdown
import os
import shutil
import tempfile
import urllib
import urllib2
import re
import random
# Create your views here.

storage = FileSystemStorage(
    location=conf.UPLOAD_PATH,
    base_url='/static/upload/'
)

alphanumeric = RegexValidator(r'^[0-9a-zA-Z\_]*$', 'Only alphanumeric characters and underscore are allowed.')


def user_info(request, user_id):
    u = User.objects.get(id=user_id)

    if not profile.objects.filter(user_id=u.id).exists():
        p = profile()
        p.user = u
        p.save()

    return render_to_response('account/user-info.html', {'request': request, 'title': _('user info'),
                                                 'user': u, 'conf': conf,
                                                 'topics': u.profile.latest_activity()['topic'],
                                                 'post_list_title': _('%s\'s topics') % (u.profile.username())})



def reg(request):
    if request.method == 'GET':
        return render_to_response('account/reg.html', {'conf': conf, 'title': _('register')},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        try:
            alphanumeric(username)
        except:
            messages.add_message(request, messages.WARNING,_('username can only contain letters digits and underscore'))
            return HttpResponseRedirect(reverse('reg'))

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.WARNING, _('username already exists'))
            return HttpResponseRedirect(reverse('reg'))

        if password != password2 or password == '' or password2 == '':
            messages.add_message(request, messages.WARNING, _('passwords don\'t match, or are blank'))
            return HttpResponseRedirect(reverse('reg'))

        user = User.objects.create_user(username, email, password)
        user = authenticate(username=username, password=password)
        login(request, user)
        p = profile()
        p.user = user
        p.save()
        return HttpResponseRedirect(reverse('index'))


def user_login(request):
    if request.method == 'GET':
        return render_to_response('account/login.html', {'conf': conf, 'title': _('sign in')},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if not User.objects.filter(username=username).exists():
            messages.add_message(request, messages.WARNING, _('username does not exist'))
            return HttpResponseRedirect(reverse('signin'))

        if user is None:
            messages.add_message(request, messages.WARNING, _('password is invalid'))
            return HttpResponseRedirect(reverse('signin'))

        login(request, user)
        return HttpResponseRedirect(reverse('index'))


def setting(request):
    if request.method == 'GET':
        return render_to_response('account/user-setting.html', {'request': request,
                                                        'conf': conf,
                                                        'title': _('settings')},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        request.user.profile.website = request.POST['website']
        request.user.email = request.POST['email']
        request.user.profile.save()
        request.user.save()
        return render_to_response('account/user-setting.html', {'request': request,
                                                        'conf': conf,
                                                        'title': _('settings')},
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
    return render_to_response('account/user-mention.html', {'request': request, 'title': _('mentions'),
                                                    'conf': conf,
                                                    'new': new,
                                                    'old': old, },
                              context_instance=RequestContext(request))


def change_password(request):
    u = request.user
    if request.method == 'GET':
        return render_to_response('account/change-password.html', {'request': request, 'title': _('change password'),
                                                           'conf': conf},
                                  context_instance=RequestContext(request))
    elif request.method == 'POST':
        old = request.POST['old-password']
        new = request.POST['password']
        if request.POST['password'] != request.POST['password2'] or request.POST['password'] == '' or request.POST['password2'] == '':
            messages.add_message(request, messages.WARNING, _('passwords don\'t match, or are blank'))
            return HttpResponseRedirect(reverse('change_password'))

        if authenticate(username=u.username, password=old):
            u.set_password(new)
            u.save()
            messages.add_message(request, messages.SUCCESS, _('password updated successfully'))
            return HttpResponseRedirect(reverse('change_password'))
        else:
            messages.add_message(request, messages.WARNING, _('unable to change your password, the current password may be invalid'))
            return HttpResponseRedirect(reverse('change_password'))


def user_avatar(request):
    u = request.user
    if request.method == 'GET':
        return render_to_response('account/user-avatar.html', {'request': request, 'title': _('avatar setting'),
                                                       'conf': conf},
                                  context_instance=RequestContext(request))
    else:
        use_gravatar = request.POST.getlist('gravatar') == ['true']
        request.user.profile.use_gravatar = use_gravatar
        f = request.FILES.get('file', None)
        if f:
            extension = os.path.splitext(f.name)[-1]
            if f.size > 524288:
                return error(request, _('file too big'))
            if (extension not in ['.jpg', '.png', '.gif']) or ('image' not in f.content_type):
                return error(request, _('file type not permitted'))
            im = Image.open(f)
            im.thumbnail((120,120))
            name = storage.get_available_name(str(u.id)) + '.png'
            url = storage.url(name)
            request.user.profile.avatar_url = url
            im.save('%s/%s' % (storage.location, name), 'PNG')
        u.profile.save()
        return HttpResponseRedirect(reverse('user_avatar'))


def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='account/reset-password-confirm.html',
        uidb64=uidb64, token=token, post_reset_redirect=reverse('signin'))


def reset(request):
    return password_reset(request, template_name='account/reset-password.html',
        email_template_name='account/reset-password-email.html',
        subject_template_name='account/reset-password-subject.txt',
        post_reset_redirect=reverse('signin'))


#def set_lang(request):
#    # the lang_code must be in the LANGUAGES tuple
#    if request.method == 'GET':
#        lang_code = request.GET['lang']
#        if hasattr(request, 'session'):
#            request.session[LANGUAGE_SESSION_KEY] = lang_code
#        else:
#            pass
#            #response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code,
#            #                    max_age=settings.LANGUAGE_COOKIE_AGE,
#            #                    path=settings.LANGUAGE_COOKIE_PATH,
#            #                    domain=settings.LANGUAGE_COOKIE_DOMAIN)
#        return HttpResponseRedirect(request.META['HTTP_REFERER'])

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
        if (not request.GET['code']) or (request.GET['state'] != 'fairybbs'):
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
