#!/usr/bin/env python
# coding:utf-8

import os
import logging
import random

from django.conf import settings
from django.http import HttpResponse
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from student.cookies import set_user_info_cookie
from openedx.core.djangoapps.theming.helpers import get_template_path
from mako.exceptions import TopLevelLookupException, TemplateLookupException
from edxmako.shortcuts import render_to_response as mako_render_to_response
from xblockutils.resources import ResourceLoader

from helpers import (
    get_subscription_content_items,
    get_recommeded_content_items,
    get_bookmarked_items,
    get_viewed_items,
    get_popular_items
)

log = logging.getLogger(__name__)
loader = ResourceLoader(__name__)


def render_to_response(template_path, context):
    try:
        response = mako_render_to_response(template_path, context)
    except TopLevelLookupException:
        try:
            template = loader.render_mako_template(os.path.join('templates/', template_path), context)
            response = HttpResponse(template)
        except TemplateLookupException as err:
            log.error("TemplateLookupException: %s", err)
            response = HttpResponse()
    return response


@login_required
@ensure_csrf_cookie
def dashboard(request):
    context = get_subscription_content_items(request)
    if context['content_items'] is not None:
        context['bookmarks'] = get_bookmarked_items(request, context['content_items'])
        context['viewed'], context['last_viewed'] = get_viewed_items(request, context['content_items'])
        source = context['last_viewed'][0] if context['last_viewed'] is not None else random.choice(context['content_items'].keys())
        context['recommendations'] = get_recommeded_content_items(request, context['content_items'], source)
    response = render_to_response('subscription_content/dashboard.html', context)
    set_user_info_cookie(response, request)
    return response


@login_required
def explore(request):
    context = get_subscription_content_items(request)
    if context['content_items'] is not None:
        context['bookmarks'] = get_bookmarked_items(request, context['content_items'])
        context['viewed'], context['last_viewed'] = get_viewed_items(request, context['content_items'])
        source = context['last_viewed'][0] if context['last_viewed'] is not None else random.choice(context['content_items'].keys())
        context['recommendations'] = get_recommeded_content_items(request, context['content_items'], source)
        context['popular'] = get_popular_items(request, context['viewed'])
    response = render_to_response('subscription_content/explore.html', context)
    set_user_info_cookie(response, request)
    return response