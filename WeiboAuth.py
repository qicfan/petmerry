#encoding:utf-8
__author__ = 'qicfan'

import logging
import time
import urllib
import mimetools
from tornado import httpclient
from tornado.httputil import HTTPHeaders
from tornado import escape
from tornado.auth import OAuthMixin,OAuth2Mixin

_CONTENT_TYPES = { '.png': 'image/png', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.jpe': 'image/jpeg' }

def _guess_content_type(ext):
	return _CONTENT_TYPES.get(ext, 'application/octet-stream')

def encode_multipart(kw):
	'''
	Build a multipart/form-data body with generated random boundary.
	'''
	boundary = mimetools.choose_boundary()
	data = []
	for k, v in kw.iteritems():
		data.append('--%s' % boundary)
		if hasattr(v, 'read'):
			ext = ''
			filename = getattr(v, 'name', '')
			n = filename.rfind('.')
			if n != (-1):
				ext = filename[n:].lower()
			content = v.read()
			data.append('Content-Disposition: form-data; name="%s"; filename="hidden"' % k)
			data.append('Content-Type: %s' % _guess_content_type(ext))
			data.append('Content-Length: %d' % len(content))
			data.append('Content-Transfer-Encoding: binary')
			data.append('')
			data.append(content)
		else:
			data.append('Content-Disposition: form-data; name="%s";Content-Type: text/plain\r\n' % k)
			data.append('')
			data.append(v.encode('utf-8') if isinstance(v, unicode) else v)
	data.append('--%s--' % boundary)
	return '\r\n'.join(data), boundary


class WeiboMixin(OAuth2Mixin):
	"""Weibo OAuth2.o authentication.(recommended)

	When your application is set up, you can use this Mixin like this
	to authenticate the user with Weibo and get access to their stream:

	class WeiboHandler(tornado.web.RequestHandler,WeiboMixin):

		@tornado.web.asynchronous
		def get(self):
			if self.get_argument("code", None):
				self.get_authenticated_user(
				  redirect_uri='/weibologin',
				  client_id=self.settings["weibo_consumer_key"],
				  client_secret=self.settings["weibo_consumer_secret"],
				  code=self.get_argument("code"),
				  callback=self.async_callback(
					self._on_auth))
				return
			self.authorize_redirect(redirect_uri='/weibologin',
									client_id=self.settings["weibo_consumer_key"])

		def _on_auth(self, user):
			if not user:
				raise tornado.web.HTTPError(500, "Weibo auth failed")
			# Save the user using, e.g., set_secure_cookie()
	"""
	_OAUTH_ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"
	_OAUTH_AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"
	_OAUTH_NO_CALLBACKS = False

	def get_authenticated_user(self, redirect_uri, client_id, client_secret,
							   code, callback, extra_fields=None):
		"""Handles the login for the Weibo user, returning a user object."""
		http = httpclient.AsyncHTTPClient()
		args = {
			"redirect_uri": redirect_uri,
			"code": code,
			"client_id": client_id,
			"client_secret": client_secret,
			}

		fields = set(['uid','id', 'name', 'screen_name', 'province',
					  'city', 'location', 'description','url',
					  'profile_image_url','gender'])
		if extra_fields: fields.update(extra_fields)
		http.fetch(self._oauth_request_token_url(**args),
			self.async_callback(self._on_access_token, redirect_uri, client_id,
				client_secret, callback, fields),
			method="POST",body=urllib.urlencode(args)
		)

	def _on_access_token(self, redirect_uri, client_id, client_secret,
						 callback, fields, response):
		if response.error:
			logging.warning('Weibo auth error: %s' % str(response))
			callback(None)
			return

		args = escape.json_decode(response.body)
		session = {
			"access_token": args["access_token"],
			"expires_in": args["expires_in"],
			"uid":args["uid"]
		}

		self.weibo_request(
			path="users/show",
			callback=self.async_callback(
				self._on_get_user_info, callback, session, fields),
			access_token=session["access_token"],
			uid=session["uid"]
		)

	def _on_get_user_info(self, callback, session, fields, user):
		if user is None:
			callback(None)
			return

		fieldmap = {}

		for field in fields:
			fieldmap[field] = user.get(field)

		fieldmap.update({"access_token": session["access_token"], "session_expires": session.get("expires_in")})
		callback(fieldmap)

	def is_expires(self, access_token, expires_in):
		if expires_in and access_token:
			return time.time() > float(expires_in)
		else:
			return True

	def weibo_request(self, path, callback, access_token=None, expires_in=None,
					  post_args=None, **args):
		url = "https://api.weibo.com/2/" + path + ".json"
		all_args = {}
		if access_token:
			all_args['access_token'] = access_token
		all_args.update(args)
		all_args.update(post_args or {})
		header = HTTPHeaders({'Authorization': 'OAuth2 %s' % access_token})
		callback = self.async_callback(self._on_weibo_request, callback)
		http = httpclient.AsyncHTTPClient()
		if post_args is not None:
			has_file = False
			for key,value in post_args.iteritems():
				if hasattr(value,"read"):
					has_file = True
			if has_file:
				post_args,boundary = encode_multipart(post_args)
				header.add('Content-Type', 'multipart/form-data; boundary=%s' %boundary)
				header.add('Content-Length', len(post_args))
				http.fetch(url, method="POST", body=post_args,
					callback=callback,headers=header)
			else:
				http.fetch(url, method="POST", body=urllib.urlencode(all_args),
					callback=callback,headers=header)
		else:
			if all_args: url += "?" + urllib.urlencode(all_args)
			http.fetch(url, callback=callback,headers=header)

	def _on_weibo_request(self, callback, response):
		if response.error:
			logging.warning("Error response %s %s fetching %s", response.error,response.body,
				response.request.url)
			callback(None)
			return
		callback(escape.json_decode(response.body))