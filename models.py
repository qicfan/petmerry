#!/usr/bin/env python
#coding=utf-8
# 实现了MVC中的模型层

__authors__ = ['"zeroq" <qicfan@gmail.com>']

import bson
import pymongo
import sys
import tornado


class ModelBase(object):
	"""
	模型基类
	实现了到mongodb的连接
	实现了基本的get、save、delete方法
	"""
	_db = None
	_table = None
	_id = None
	
	def __init__(self):
		self.__parse_fields()
		return
	
	def __setattr__(self, name, value):			
		if not hasattr(self, name) and not self._fields.has_key(name):
			raise tornado.web.HTTPError(500, '%s not has attrbite: %s' % (self.__class__.__name__, name))
		if self._fields.has_key(name):
			self._fields[name] = value
		setattr(self.__class__, name, value)
		return
	
	def __parse_fields(self):
		for key in self._fields:
			setattr(self.__class__, key, self._fields[key])
		return
	
	@property
	def db(self):
		"""
		建立到mongodb的连接
		"""
		if self._db == None:
			self._db = pymongo.Connection(host='127.0.0.1', 
										  port=27018, maxcached=10, 
										  maxconnections=50, dbname='test')
			self._db = self._db.test
		return self._db
	
	@property
	def tb(self):
		if self._table == None:
			self._table = self.db[self.__class__.__name__]
		return self._table

	def save(self):
		return self.tb.insert(self._fields)
	
	def delete(self):
		return
	
	def get(self):
		return 'aa'
	
	def getAll(self):
		return
	
	def getId(self, id):
		return bson.objectid.ObjectId(self._id)

class Category(ModelBase):
	"""
	分类模型
	新建一个分类：
	>>> category = Category()
	>>> category.category_name = u'cat1'
	>>> category.parent_id = 0
	>>> category.create_time = u'2012-07-09 18:00:00'
	>>> category.save()
	修改一个分类
	>>> category = Category.find(1)
	>>> category.category_name = u'cat2'
	>>> category.save()
	Attributes:
		_fields: 字段map 
	"""
	
	_fields = {
		'category_name': None,
		'parent_id': None,
		'create_time': None,
		}
