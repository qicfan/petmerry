#!/usr/bin/env python
#coding:utf-8

__author__="qicfan"
__date__ ="$2012-8-13 17:09:09$"

import tornado
import uuid

class SessionData(dict):
	id = None
	
	def __init__(self, id=None):
		self.id = id
		return
	
	def save(self):
		return
		
session = SessionData()
session.id = uuid.uuid1()
session['key'] = 'value'
print session
