#!/usr/bin/env python
# coding:utf-8

import json
import requests
import logging

from django.core.cache import cache

log = logging.getLogger(__name__)

# Token Endpoint
def get_access_token(client_id, client_secret):
	'''
	Get access token from Bibblio
	'''
	headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
	payload = {
		'client_id': client_id,
		'client_secret': client_secret
	}
	cache_key = 'bibblio_get_access_token'
	token = cache.get(cache_key)
	if token is None:
		request = requests.post('https://api.bibblio.org/v1/token', data=payload, headers=headers)
		if request.status_code == 200:
			response = request.json()
			if 'access_token' in response:
				cache.set(cache_key, response['access_token'], int(response['expires_in'])-1)
				return response
	else:
		return { 'access_token': token }
	return {'status': request.status_code, "message": request.text}


def get_catalogues(access_token, limit=10, page=1):
	'''
	Get all content catalogues
	'''
	headers = { 'Authorization': 'Bearer '+access_token }
	url = 'https://api.bibblio.org/v1/catalogues'
	params = {
		'limit': limit,
		'page': page
	}

	cache_key = 'bibblio_get_catalogues'
	content = cache.get(cache_key)
	if content is None:
		request = requests.get(url, params=params, headers=headers)
		if request.status_code == 200:
			content = request.json()
			cache.set(cache_key, content, 60*60)
		else:
			return {'status': request.status_code, "message": request.text}
	return content


def get_content_items(access_token, catalogueIds=[], limit=10, page=1):
	'''
	Get all content items from a specified catalogue
	'''
	headers = { 'Authorization': 'Bearer '+access_token }
	url = 'https://api.bibblio.org/v1/content-items'
	params = {
		'catalogueId': None,
		'fields': 'url,name,headline,description,timeRequired,thumbnail,moduleImage,image,keywords',
		'limit': limit,
		'page': page
	}

	cache_key = 'bibblio_get_content_items_'+str(catalogueIds)
	content = cache.get(cache_key)
	if content is None:
		content = { 'results': [] }
		for catalogueId in catalogueIds:
			params['catalogueId'] = catalogueId
			request = requests.get(url, params=params, headers=headers)
			if request.status_code == 200:
				content['results'].extend(request.json()['results'])
				cache.set(cache_key, content, 60*60)
			else:
				return {'status': request.status_code, "message": request.text}
	return content


def get_content_item(access_token, contentItemId):
	'''
	Get a specific content item
	'''
	headers = { 'Authorization': 'Bearer '+str(access_token) }
	url = 'https://api.bibblio.org/v1/content-items/'+str(contentItemId)

	cache_key = 'bibblio_get_content_item_'+str(contentItemId)
	content = cache.get(cache_key)
	if content is None:
		request = requests.get(url, headers=headers)
		if request.status_code == 200:
			content = request.json()
			cache.set(cache_key, content, 60*60)
		else:
			return {'status': request.status_code, "message": request.text}

	return content


def get_recommedations(recommendation_key, userId, contentItemId):
	'''
	Get recommedations for user
	'''
	headers = { 'Authorization': 'Bearer '+str(recommendation_key) }
	url = 'https://api.bibblio.org/v1/recommendations'
	params = {
		'userId': userId,
		'contentItemId': contentItemId,
		'fields': 'url,name,headline,description,timeRequired,thumbnail,moduleImage,image,keywords'
	}

	cache_key = 'bibblio_get_recommendations_'+str(userId)
	content = cache.get(cache_key)
	if content is None:
		request = requests.get(url, params=params, headers=headers)
		if request.status_code == 200:
			cache.set(cache_key, request.json(), 15*60)
			return request.json()
		else:
			return {'status': request.status_code, "message": request.text}

	return content


def track_activity(access_token, contextId, contentItemId, userId, sourceHref):
	'''
	Get all content items from a specified catalogue
	'''
	headers = { 'Authorization': 'Bearer '+str(access_token) }
	url = 'https://api.bibblio.org/v1/activities/'+str(contextId)
	payload = {
		'type': 'Viewed',
		'object': {[ 'contentItemId', contentItemId ]},
		'context': {[ 'sourceHref', sourceHref ]},
		'actor': { 'userId': userId	}
	}

	request = requests.post(url, data=payload, headers=headers)
	if request.status_code == 200:
		return request.json()
	else:
		return {'status': request.status_code, "message": request.text}
