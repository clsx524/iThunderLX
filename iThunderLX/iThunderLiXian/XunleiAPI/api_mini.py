#author: MartianZ <fzyadmin@gmail.com>
#Edited by Eric <clsx524@gmail.com>
import socket
import random
import requests
from hashlib import md5
from lixian_api import LiXianAPI, determin_url_type
import tornado.ioloop
import tornado.web
from time import time
from datetime import datetime
import json
import os

def hex_md5(string):
    return md5(string).hexdigest()

def thunder_login(username, password, secure, hashstr):
	if not secure:
		hash = hex_md5(username + password + username)
	else:
		hash = hashstr

	lixianAPI = LiXianAPI()
	
	try:
		if secure:
			isLogin = lixianAPI.secure_login(username, password)
		else:
			isLogin = lixianAPI.login(username, password)
	except:
		isLogin = False
	
	if isLogin:
		print 'USER LOGIN SUCCESS: ' + username
		try:
			if not secure:
				#save user info
				print pyfile_dir
				
				f = open(pyfile_dir + '/.iThunderLX_' + hash +'.txt', 'w')
				f.truncate(0)
				f.write(username + '\n' + hex_md5(hex_md5(password)))
				f.close()
				
				pass
		except:
			pass
				
		lixianAPIs[hash] = lixianAPI
		lixianAPIs_login_status[hash] = True
		lixianAPIs_last_update_time[hash] = time()
		
		return True
	else:
		print 'USER LOGIN FAIL: ' + username
		return False

def check_login(hash):
	isLogin = False
		
	if lixianAPIs.get(hash):
		lixianAPI = lixianAPIs.get(hash)
		if time() - lixianAPIs_last_update_time.get(hash) < 300:
			isLogin = lixianAPIs_login_status.get(hash)
		else:
			isLogin = lixianAPI.check_login()
			lixianAPIs_login_status[hash] = isLogin
			lixianAPIs_last_update_time[hash] = time()
			
	if not isLogin:
		f = open(pyfile_dir + '/.iThunderLX_' + hash + '.txt', 'r')
		username = f.readline()[0:-1]
		password = f.readline()
		f.close()
		if username and password:
			isLogin = thunder_login(username, password, True, hash)

	return isLogin

class InitialHandler(tornado.web.RequestHandler):
	def get(self, username, password):
		hash = hex_md5(username + password + username)
		
		if thunder_login(username, password, False, ''):
			self.write(hash)
		else:
			self.write('Fail')


class GetTaskListHandler(tornado.web.RequestHandler):
	def get(self, hash, limit, st):
	
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
			
		lixianAPI = lixianAPIs.get(hash)
		
		tasklist = lixianAPI.get_task_list(int(limit), int(st))
		tasklist_json = json.dumps(tasklist)
		self.write(tasklist_json)

            #class AddBTTaskHandler(tornado.web.RequestHandler):
            #def get(self, hash, path):
            #	self.write("POST HERE")
    
            #def post(self):
            #hash = self.get_argument("hash")
            #path = self.get_argument("path")
            #isLogin = check_login(hash)
            #if not isLogin:
            #	self.write("LFail")
            #	self.finish()
            #	return
        
            #lixianAPI = lixianAPIs.get(hash)
            #if lixianAPI.add_bt_task_by_path(path):
            #	self.write("Success")
            #else:
            #	self.write("ADDFail")

class AddTaskHandler(tornado.web.RequestHandler):
	def get(self, hash, url):
		self.write("POST HERE")
    
	def post(self):
		hash = self.get_argument("hash")
		url = self.get_argument("url")
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
        
		lixianAPI = lixianAPIs.get(hash)
		if lixianAPI.add(url):
			self.write("Success")
		else:
			self.write("Fail")

class DeleteTaskHandler(tornado.web.RequestHandler):
	def get(self, hash, task_ids):
		self.write("POST HERE")
    
	def post(self):
		hash = self.get_argument("hash")
		task_ids = self.get_argument("tid")
		isLogin = check_login(hash)
		if not isLogin:
			self.write("LoginFail")
			self.finish()
			return
        
		lixianAPI = lixianAPIs.get(hash)
		if lixianAPI.task_delete(task_ids):
			self.write("DeleteSuccess")
		else:
			self.write("DeleteFail")

class GetTorrentFileListHandler(tornado.web.RequestHandler):
	def get(self, hash, url):
		self.write("POST HERE")
    
	def post(self):
		hash = self.get_argument("hash")
		url = self.get_argument("url")
        
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
        
		lixianAPI = lixianAPIs.get(hash)
		filelist = lixianAPI.torrent_upload_by_path(url)
		self.write(json.dumps(filelist))

class AddBTTaskHandler(tornado.web.RequestHandler):
	def get(self, hash, url):
		self.write("POST HERE")
    
	def post(self):
		hash = self.get_argument("hash")
		info = json.loads(self.get_argument("info"))
		url = self.get_argument("url")
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
		lixianAPI = lixianAPIs.get(hash)
		if lixianAPI.add_bt_task_with_dict(url,info):
			self.write("Success")
		else:
			self.write("Fail")


class GetBTListHandler(tornado.web.RequestHandler):
	def get(self, hash, tid, cid):
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
        
		lixianAPI = lixianAPIs.get(hash)
		result = lixianAPI.get_bt_list(int(tid), cid)
		self.write(json.dumps(result))

class GetCookieHandler(tornado.web.RequestHandler):
	def get(self, hash):
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
			
		lixianAPI = lixianAPIs.get(hash)
		self.write("gdriveid=" + lixianAPI.gdriveid + ";")

class VodGetPlayUrl(tornado.web.RequestHandler):
	def get(self):
		self.write("POST HERE")
		
	def post(self):
		print self.request.arguments
		hash = self.get_argument("hash")
		url = self.get_argument("url")
		
		isLogin = check_login(hash)
		if not isLogin:
			self.write("Fail")
			self.finish()
			return
		
		print url
		lixianAPI = lixianAPIs.get(hash)
		self.write(lixianAPI.cloud_play_get_url(url))
		
		
class ZeroHandler(tornado.web.RequestHandler):
	def get(self, hash):
		self.write("Mitsukatta~~ToT")



application = tornado.web.Application([
	(r'/initial/(.*)/(.*)', InitialHandler),  #API 1
	(r'/([A-Za-z0-9]{32})/get_task_list/([0-9]*)/([0-9]*)', GetTaskListHandler), #API 2
	(r'/add_task', AddTaskHandler), #API 3
    (r'/add_bt_task', AddBTTaskHandler), #API 4
    (r'/task_delete',DeleteTaskHandler), #API 5
    (r'/([A-Za-z0-9]{32})/get_bt_list/(.*)/(.*)', GetBTListHandler), #API 6 TID CID
    (r'/get_torrent_file_list', GetTorrentFileListHandler), #API 7    
    (r'/([A-Za-z0-9]{32})/get_cookie',  GetCookieHandler),
	(r'/vod_get_play_url', VodGetPlayUrl),
	(r'(.*)', ZeroHandler),  #API Zero

])


if __name__ == "__main__":
	
	pyfile_dir = os.path.split(os.path.realpath(__file__))[0]
	print pyfile_dir
	lixianAPIs = {}
	lixianAPIs_login_status = {}
	lixianAPIs_last_update_time = {}
	
	
	application.listen(9999)
	print "The Thunder API Sutato!"
	
	tornado.ioloop.IOLoop.instance().start()