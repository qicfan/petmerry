#!/usr/bin/env python
#coding=utf-8

__authors__ = ['"zeroq" <qicfan@gmail.com>']

import os
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.web
import WeiboAuth


settings = {
	"title": "PetMerry",
	"debug": True,
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	"cookie_secret": "MTEyMjMzNDQ1NTY2Nzc4ODk5MDAxMTIyMzM0NDU1NjY3Nzg4OTkwMDExMjIzMzQ0NDU2Njc3ODg5OTAwMTEyMg==",
	"login_url": "/login",
	"template_path": os.path.join(os.path.dirname(__file__), "templates/default"),
	"log_file_prefix": os.path.join(os.path.dirname(__file__), "logs"),
	"weibo_consumer_key": "4242429219",
	"weibo_consumer_secret": "3e56a76238dcdddb0793b6be7f982604",
}


class WebBase(tornado.web.RequestHandler):
	"""
	petmerry网站基类
	"""
	
	def get_template_path(self):
		"""
		重写了get_template_path方法，模板统一放置在templates文件夹下，并且可以使用不同的主题
		"""
		
		return settings['template_path']
	
	def render(self, template_name, **kwargs):
		"""
		重写render方法，统一传入title等，统一网站标题
		"""
		
		return super(WebBase, self).render(template_name, title=settings['title'], **kwargs)


class MainHandler(WebBase):
	"""
	处理首页请求
	"""
	
	def get(self):
		self.render("index.html")


class LoginHandler(WebBase):
	"""
	处理登录请求
	"""
	
	def get(self):
		"""
		显示登录页面
		"""
		return


class GoogleHandler(WebBase, tornado.auth.GoogleMixin):
	"""
	使用谷歌账户登录
	"""

	@tornado.web.asynchronous
	def get(self):
		if self.get_argument("openid.mode", None):
			self.get_authenticated_user(self.async_callback(self._on_auth))
			return
		self.authenticate_redirect()

	def _on_auth(self, user):
		if not user:
			raise tornado.web.HTTPError(500, "Google auth failed")
		# Save the user with, e.g., set_secure_cookie()


class WeiboHandler(WebBase, WeiboAuth.WeiboMixin):
	"""
	 使用微博账户登录
	 """
	@tornado.web.asynchronous
	def get(self):
		if self.get_argument("code", None):
			self.get_authenticated_user(
				redirect_uri='/weibologin',
				client_id=self.settings["weibo_consumer_key"],
				client_secret=self.settings["weibo_consumer_secret"],
				code=self.get_argument("code"),
				callback=self.async_callback(self._on_auth)
			)
			return
		self.authorize_redirect(redirect_uri='/weibologin',
			client_id=self.settings["weibo_consumer_key"])

	def _on_auth(self, user):
		if not user:
			raise tornado.web.HTTPError(500, "Weibo auth failed")
		# Save the user using, e.g., set_secure_cookie()


application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/login", LoginHandler),
	(r"/login/weibo", WeiboHandler),
	(r"/login/google", GoogleHandler),
	(r"/static", tornado.web.StaticFileHandler),
], **settings)

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()