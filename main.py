#!/usr/bin/env python
#coding=utf-8

__authors__ = ['"zeroq" <qicfan@gmail.com>']

import models
import os
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.web
import time
import WeiboAuth


settings = {
	"title": "报名系统",
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
		apply_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))
		basket = models.BasketBall.collection.find({"date": apply_time})
		if not self.get_secure_cookie("apply_name"):
			username = ""
		else:
			username = self.get_secure_cookie("apply_name")
		self.render("index.html", data = basket, apply_time = apply_time, count = basket.count(), username = username)

	def post(self):
		arg = self.request.arguments
		if "name" not in arg:
			self.alert(u"不输入名字不能报名!", "/")
		apply_time = time.strftime('%Y-%m-%d',time.localtime(time.time()))

		username = self.get_argument("name").strip()
		# 判断用户名长度
		if len(username) > 10:
			self.alert(u"你名字真有那么长吗？", "/")
			return
		if len(username) == 0:
			self.alert(u"输入空格很可耻啊!", "/")
			return
		# 判断今日是否已经报名
		user = models.BasketBall.collection.find_one({'date': apply_time, 'username': username})
		if user != None:
			self.alert(u"%s, 你已经报名参加今天的比赛了，不需要重复报名" % username, "/")
			return
		basket = models.BasketBall({"username": username, "addtime": time.strftime('%Y-%m-%d %X',time.localtime(time.time())), "date": apply_time})
		basket.save()
		self.set_secure_cookie("apply_name", username)
		self.alert("thanks, %s" % username, "/")
		return

	def alert(self, message, url):
		self.write("<script type='text/javascript'>alert('%s'); window.location='%s'; </script>" % (message, url))
		self.finish()


application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/static", tornado.web.StaticFileHandler),
], **settings)

if __name__ == "__main__":
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	tornado.ioloop.IOLoop.instance().start()