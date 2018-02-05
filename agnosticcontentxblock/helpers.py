#!/usr/bin/env python
# coding:utf-8

import re
import logging

from datetime import datetime
from django.conf import settings
from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.bookmarks import api as bookmarks_api
from openedx.core.djangoapps.content.block_structure.api import get_course_in_cache
from student.views import is_course_blocked, get_org_black_and_whitelist_for_site, get_course_enrollments
from opaque_keys.edx.keys import CourseKey, UsageKey
from courseware.user_state_client import DjangoXBlockUserStateClient
from courseware.model_data import DjangoKeyValueStore, FieldDataCache
from opaque_keys.edx.locator import BlockUsageLocator, CourseLocator
from xblock.fields import Scope

from api import get_access_token, get_catalogues, get_content_items, get_content_item, get_recommedations

log = logging.getLogger(__name__)


def get_xblock_settings():
    xblock_settings = configuration_helpers.get_value('XBLOCK_SETTINGS', settings.XBLOCK_SETTINGS)
    if xblock_settings:
        if 'bibblio' in xblock_settings:
            return xblock_settings['bibblio']
    return {
        'recommendation_key': '',
        'client_secret': '',
        'client_id': ''
    }


def get_course_keys(user):
        site_org_whitelist, site_org_blacklist = get_org_black_and_whitelist_for_site(user)
        course_enrollments = list(get_course_enrollments(user, site_org_whitelist, site_org_blacklist))
        course_enrollments.sort(key=lambda x: x.created, reverse=True)
        return [ enrollment.course_id for enrollment in course_enrollments ]


def get_subscription_catalog_id(course_id, mode):
        course_store = modulestore().get_course(course_id)
        if course_store.subscription_content_settings:
                if mode in course_store.subscription_content_settings:
                        return course_store.subscription_content_settings[mode]
        return None


def get_subscription_catalog_ids(user, course_enrollments=None):
        if not course_enrollments:
                site_org_whitelist, site_org_blacklist = get_org_black_and_whitelist_for_site(user)
                course_enrollments = list(get_course_enrollments(user, site_org_whitelist, site_org_blacklist))
                course_enrollments.sort(key=lambda x: x.created, reverse=True)
        subscription_catalog_ids = []
        for enrollment in course_enrollments:
                new_subscription_catalog_ids = get_subscription_catalog_id(enrollment.course_id, enrollment.mode)
                if new_subscription_catalog_ids:
                        subscription_catalog_ids = subscription_catalog_ids+new_subscription_catalog_ids
        return filter(None, frozenset(subscription_catalog_ids))


def get_subscription_content_items(request):
    context = {}
    settings = get_xblock_settings()
    token = get_access_token(settings['client_id'], settings['client_secret'])
    if 'access_token' in token:
        catalog_ids = get_subscription_catalog_ids(request.user)
        if catalog_ids:
            context = { 'content_items': {}, 'keywords': {}, 'bookmarks': [] }
            content_items = get_content_items(token['access_token'], catalog_ids)
            if 'results' in content_items:
                for item in content_items['results']:
                    item['blockusage_id'] = re.search(r'[a-zA-Z0-9]+$', item['url']).group()
                    for key in [ word.title() for word in item['keywords'] ]:
                        context['keywords'].setdefault(key, []).append(item['contentItemId'])
                    if not item['thumbnail'] and item['moduleImage']:
                        item['thumbnail'] = item['moduleImage']
                    context['content_items'][item['contentItemId']] = item
            else:
                log.error("Error fetching content items: %s", str(content_items['message']))
        else:
            log.warning("No subscription products found. Disable subscription?")
    else:
        log.error("Access token: %s", str(token['message']))
    return context


def get_recommeded_content_items(request, content_items, content_item_id):
    recommendations = []
    settings = get_xblock_settings()
    recommended = get_recommedations(settings['recommendation_key'], request.user.id, content_item_id)
    if 'results' in recommended:
        for recommendation in recommended['results']:
            recommendations.append(recommendation['contentItemId'])
    return recommendations


def get_bookmarked_items(request, content_items):
    bookmarks = []
    bookmarked = get_bookmarks(request)
    for bookmark in bookmarked:
        blockusage_id = re.search(r'[a-zA-Z0-9]+$', unicode(bookmark)).group()
        for contentItemId, item in content_items.iteritems():
            if blockusage_id == item['blockusage_id']:
                bookmarks.append(contentItemId)
                break
    return bookmarks


def get_bookmarks(request):
    bookmarks = []
    course_keys = get_course_keys(request.user)
    for course_key in course_keys:
        bookmarks = bookmarks + list(bookmarks_api.get_bookmarks(
            user=request.user, course_key=course_key, serialized=False
        ))
    return bookmarks


def get_user_state_summary_field(kvs, user_id, block_usage_locator, field, default):
    try:
        return kvs.get(DjangoKeyValueStore.Key(
            scope=Scope.user_state_summary,
            user_id=user_id,
            block_scope_id=block_usage_locator,
            field_name=field
        ))
    except KeyError:
        return default


def get_viewed_items(request, content_items):
    viewed = {}
    last_viewed = None
    course_keys = get_course_keys(request.user)
    for course_key in course_keys:
        course_structure = get_course_in_cache(course_key)
        course_locator = CourseLocator.from_string(unicode(course_key))
        username = request.user.username
        user_state_client = DjangoXBlockUserStateClient()
        for chapter_key in course_structure.get_children(course_structure.root_block_usage_key):
            for subsection_key in course_structure.get_children(chapter_key):
                for unit_key in course_structure.get_children(subsection_key):
                    for component_key in course_structure.get_children(unit_key):
                        for block_key in course_structure.get_children(component_key):
                            try:
                                usage_key = block_key.map_into_course(course_key)
                                user_state = user_state_client.get(username, usage_key) # returns XBlockUserState
                                if 'last_viewed' in user_state.state:
                                    blockusage_id = re.search(r'[a-zA-Z0-9]+$', unicode(usage_key)).group()
                                    for contentItemId, item in content_items.iteritems():
                                        if blockusage_id == item['blockusage_id']:
                                            if last_viewed is None or user_state.state['last_viewed'] > last_viewed[1]:
                                                last_viewed = [ contentItemId, user_state.state['last_viewed'] ]
                                            block_usage_locator = BlockUsageLocator(
                                                course_locator,
                                                'agnosticcontentxblock',
                                                block_id=item['blockusage_id']
                                            )
                                            descriptor = modulestore().get_item(usage_key)
                                            field_data_cache = FieldDataCache([descriptor], course_key, request.user)
                                            kvs = DjangoKeyValueStore(field_data_cache)
                                            viewed[contentItemId] = {
                                                'last_viewed': user_state.state['last_viewed'] if 'last_viewed' in user_state.state else None,
                                                'liked': user_state.state['liked'] if 'liked' in user_state.state else False,
                                                'views': get_user_state_summary_field(kvs, request.user.id, block_usage_locator, 'views', 0),
                                                'likes': get_user_state_summary_field(kvs, request.user.id, block_usage_locator, 'likes', 0),
                                            }
                                            break
                            except DjangoXBlockUserStateClient.DoesNotExist:
                                print('User '+str(username)+' has never accessed problem'+str(usage_key))
    return viewed, last_viewed


def get_popular_items(request, viewed_items):
    viewed_items.sort(key=lambda x: x.likes, reverse=True)
    return viewed_items