#!/usr/bin/env python
#coding=utf-8
# 实现了MVC中的模型层

__authors__ = ['"zeroq" <qicfan@gmail.com>']

from minimongo import Model, Index, configure

configure(host='127.0.0.1', port=27018, database = "test")

class BasketBall(Model):
	class Meta:
		collection = "BasketBall"
		indices = (
			Index("username"),
		)
