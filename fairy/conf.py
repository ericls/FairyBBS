#encoding=utf-8
from forum.models import node
from fairy import settings
import os
sitename = u'FairyBBS官方网站'
links = {
        #'eric': 'http://leeeric.com',
        #'jiecao': 'http://jiecao.cc',
        }
nodes = node.objects.all()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_PATH = os.path.join(BASE_DIR, 'static/upload')