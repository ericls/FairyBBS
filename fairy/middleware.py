# -*- coding: utf-8 -*-
from fairy.conf import site_off
from forum.views import error
from django.core.urlresolvers import reverse

class SiteOff(object):

    def process_request(self, request):
        if (site_off) and (request.path != reverse('signin')) and (not request.user.is_superuser):
            return error(request, 'down for maintenace')
