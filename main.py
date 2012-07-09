#!/usr/bin/env python
#coding=utf-8

__authors__ = ['"zeroq" <qicfan@gmail.com>']

import models
import tornado.httpserver
import tornado.ioloop
import tornado.web
import os


settings = {
	"title": "PetMerry",
	"debug": True,
	"static_path": os.path.join(os.path.dirname(__file__), "static"),
	"cookie_secret": "MTEyMjMzNDQ1NTY2Nzc4ODk5MDAxMTIyMzM0NDU1NjY3Nzg4OTkwMDExMjIzMzQ0NDU2Njc3ODg5OTAwMTEyMg==",
	"login_url": "/login",
	"template_path": os.path.join(os.path.dirname(__file__), "templates/default"),
	"log_file_prefix": os.path.join(os.path.dirname(__file__), "logs"),
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


class RegisterHandler(WebBase):
	"""
	处理注册请求
	"""
	
	def get(self):
		return
	
	def post(self):
		return


class LoginHandler(WebBase):
	"""
	处理登录请求
	"""
	
	def get(self):
		"""
		显示登录页面
		"""
		
		self.write("login")
		category = models.Category()
		category.category_name = 'cat1'
		category.parent_id = 0
		category.create_time = '2012-07-09 18:00:00'
		id = category.save()
		self.write(str(id))

	def post(self):
		"""
		处理登录请求
		"""
		
		return


class GoodsHandler(WebBase):
	"""
	使用谷歌账户登录
	"""
	
	def get(self):
		if self.get_argument("openid.mode", None):
			self.get_authenticated_user(self.async_callback(self._on_auth))
			return
		self.authenticate_redirect()

	def _on_auth(self, user):
		if not user:
			raise tornado.web.HTTPError(500, "Google auth failed")
	# Save the user with, e.g., set_secure_cookie()

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/login", LoginHandler),
	(r"/regsiter", RegisterHandler),
	(r"/singin", RegisterHandler),
	(r"/static", tornado.web.StaticFileHandler),
], **settings)

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()