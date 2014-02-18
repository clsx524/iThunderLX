import re
import time
import json
import logging
import requests
import xml.sax.saxutils
from hashlib import md5
from random import random, sample
from urlparse import urlparse
from pprint import pformat
from jsfunctionParser import parser_js_function_call
import urllib
import urllib2
import logging
import cookielib
import os.path
import sys

reload(sys)
sys.setdefaultencoding('utf8')

DEBUG = logging.debug

class LiXianAPIException(Exception): pass
class NotLogin(LiXianAPIException): pass
class HTTPFetchError(LiXianAPIException): pass

def hex_md5(string):
    return md5(string).hexdigest()

def parse_url(url):
    url = urlparse(url)
    return dict([part.split("=") for part in url[4].split("&")])

def is_bt_task(task):
    return task.get("f_url", "").startswith("bt:")

def determin_url_type(url):
    url_lower = url.lower()
    if url_lower.startswith("file://"):
        return "local_file"
    elif url_lower.startswith("ed2k"):
        return "ed2k"
    elif url_lower.startswith("thunder"):
        return "thunder"
    elif url_lower.startswith("magnet"):
        return "magnet"
    elif url_lower.endswith(".torrent"):
        return "bt"
    else:
        return "normal"

title_fix_re = re.compile(r"\\([\\\"\'])")
def title_fix(title):
    return title_fix_re.sub(r"\1", title)

def unescape_html(html):
	return xml.sax.saxutils.unescape(html)

def remove_bom(response):
	if response.startswith('\xef\xbb\xbf'):
		response = response[3:]
	return response

def assert_response(response, jsonp, value=1):
	response = remove_bom(response)
	print response
	assert response == '%s(%s)' % (jsonp, value), repr(response)

class LiXianAPI(object):
    DEFAULT_USER_AGENT = "User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2"
    DEFAULT_REFERER = "http://lixian.vip.xunlei.com/"
    LOGIN_URL = "http://login.xunlei.com/sec2login/"
    REDIRECT_URL = "http://dynamic.lixian.vip.xunlei.com/login"
    CHECK_URL = "http://login.xunlei.com/check?u=%(username)s&cachetime=%(cachetime)d"
    VERIFY_CODE = "http://verify2.xunlei.com/image?cachetime=%s"
    SHOWTASK_UNFRSH_URL = "http://dynamic.cloud.vip.xunlei.com/interface/showtask_unfresh"
    QUERY_URL = "http://dynamic.cloud.vip.xunlei.com/interface/url_query"
    TASK_CHECK_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_check"
    TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_commit"
    BATCH_TASK_CHECK_URL = "http://dynamic.cloud.vip.xunlei.com/interface/batch_task_check"
    BATCH_TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/batch_task_commit?callback=jsonp1234567890"
    TORRENT_UPDATE_URL = "http://dynamic.cloud.vip.xunlei.com/interface/torrent_upload"
    FILL_BT_LIST = "http://dynamic.cloud.vip.xunlei.com/interface/fill_bt_list"
    BT_TASK_COMMIT_URL = "http://dynamic.cloud.vip.xunlei.com/interface/bt_task_commit?callback=jsonp1234567890"
    TASK_DELAY_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_delay?taskids=%(ids)s&noCacheIE=%(cachetime)d"
    TASK_DELETE_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_delete"
    TASK_PAUSE_URL = "http://dynamic.cloud.vip.xunlei.com/interface/task_pause"
    REDOWNLOAD_URL = "http://dynamic.cloud.vip.xunlei.com/interface/redownload?callback=jsonp1234567890"
    GET_WAIT_TIME_URL = "http://dynamic.cloud.vip.xunlei.com/interface/get_wait_time"
    GET_FREE_URL = "http://dynamic.cloud.vip.xunlei.com/interface/free_get_url"
    GET_TASK_PROCESS = "http://dynamic.cloud.vip.xunlei.com/interface/task_process"
    SHARE_URL = "http://dynamic.sendfile.vip.xunlei.com/interface/lixian_forwarding"
    CHECK_LOGIN_URL = "http://dynamic.cloud.vip.xunlei.com/interface/verify_login"
    TASK_URL = "http://dynamic.cloud.vip.xunlei.com/user_task?userid=%s"
    LOGOUT_URL = "http://login.xunlei.com/unregister?sessionid=%(sessionid)s"
    
    VOD_REDIRECT_PLAY_URL = "http://dynamic.vod.lixian.xunlei.com/play"
    VOD_GET_PLAY_URL = "http://dynamic.vod.lixian.xunlei.com/interface/get_play_url"
    VOD_CHECK_VIP = "http://dynamic.vod.lixian.xunlei.com/interface/check_vip"
    VOD_GET_BT_LIST = "http://dynamic.vod.lixian.xunlei.com/interface/get_bt_list"
    VOD_GET_LIST_PIC = "http://dynamic.vod.lixian.xunlei.com/interface/get_list_pic"
    VOD_GET_BT_PIC = "http://i.vod.xunlei.com/req_screenshot?jsonp=%(jsonp)s&info_hash=%(info_hash)s&req_list=%(req_list)s&t=%(t)s"
    VOD_GET_PROCESS = "http://dynamic.vod.lixian.xunlei.com/interface/get_progress/"
    
    WEBFILEMAIL_INTERFACE_URL = "http://kuai.xunlei.com/webfilemail_interface"
    VIP_INFO_URL = "http://dynamic.vip.xunlei.com/login/asynlogin_contr/asynProxy/"
    CLOUD_PLAY_GET_URL = "http://i.vod.xunlei.com/req_get_method_vod"
    
    d_status = { 0: "waiting", 1: "downloading", 2: "finished", 3: "failed", 5: "paused" }
    d_tasktype = {0: "bt", 1: "normal", 2: "ed2k", 3: "thunder", 4: "magnet" }
    st_dict = {"unknow": 0, "downloading": 1, "finished": 2, "unknow": 3, "all": 4}
    
    def __init__(self, user_agent = DEFAULT_USER_AGENT, referer = DEFAULT_REFERER):
        self.session = requests.session()
        self.session.headers['User-Agent'] = user_agent
        self.session.headers['Referer'] = referer
        
        self.islogin = False
        self.task_url = None
        self.uid = 0
        self.username = ""
    
    def urlopen(self, url, **args):
		if 'data' in args and type(args['data']) == dict:
			args['data'] = urllib.urlencode(args['data'])
		return self.session.opener.open(urllib2.Request(url, **args), timeout=60)
    
    def login(self, username, password, verifycode = None):
        self.username = username
        verifycode = verifycode or self._get_verifycode(username)
        login_data = dict(
                          u = username,
                          p = hex_md5(hex_md5(hex_md5(password))+verifycode.upper()),
                          verifycode = verifycode,
                          login_enable = 1,
                          login_hour = 720)
        r = self.session.post(self.LOGIN_URL, login_data)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        
        self.islogin = self._redirect_to_user_task() and self.check_login()
        return self.islogin
    
    def secure_login(self, username, secure_password):
        self.username = username
        verifycode = self._get_verifycode(username)
        login_data = dict(
                          u = username,
                          p = hex_md5(secure_password+verifycode.upper()),
                          verifycode = verifycode,
                          login_enable = 1,
                          login_hour = 720)
        r = self.session.post(self.LOGIN_URL, login_data)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        
        self.islogin = self._redirect_to_user_task() and self.check_login()
        return self.islogin
    
    @property
    def _now(self):
        return int(time.time()*1000)
    
    @property
    def _random(self):
        return str(self._now)+str(random()*(2000000-10)+10)
    
    def _get_verifycode(self, username):
        r = self.session.get(self.CHECK_URL %
                             {"username": username, "cachetime": self._now})
        r.raise_for_status()
        
        verifycode_tmp = r.cookies['check_result'].split(":", 1)
        assert 2 >= len(verifycode_tmp) > 0, verifycode_tmp
        if verifycode_tmp[0] == '0':
            return verifycode_tmp[1]
        else:
            return None
    
    def verifycode(self):
        r = self.session.get(self.VERIFY_CODE % self._now)
        return r.content
    
    def _redirect_to_user_task(self):
        r = self.session.get(self.REDIRECT_URL)
        r.raise_for_status()
        gdriveid = re.search(r'id="cok" value="([^"]+)"', r.content).group(1)
        if not gdriveid:
            return False
        cookie = self.get_cookie()
        self.gdriveid = gdriveid
        self.uid = int(cookie['userid'])
        self.isvip = cookie['isvip']
        self.nickname = cookie['nickname']
        self.task_url = self.TASK_URL % self.uid
        return True
    
    def _get_task_list(self, pagenum, st):
        self.session.cookies["pagenum"] = str(pagenum)
        r = self.session.get(self.SHOWTASK_UNFRSH_URL, params={
                             "callback": "json1234567890",
                             "t": self._now,
                             "type_id": st,
                             "page": 1,
                             "tasknum": pagenum,
                             "p": 1,
                             "interfrom": "task"})
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0] if args else {}
    
    def get_task_list(self, pagenum=10, st=4):
        st = 4 if (st==0) else st
        if isinstance(st, basestring):
            st = self.st_dict[st]
        raw_data = self._get_task_list(pagenum, st)['info']['tasks']
        for r in raw_data:
            r["task_id"] = int(r["id"])
            r["cid"] = r["cid"]
            r["url"] = r["url"]
            r["taskname"] = r["taskname"]
            r["task_type"] = self.d_tasktype.get(int(r["tasktype"]), 1)
            r["status"] = self.d_status.get(int(r["download_status"]), "waiting")
            r["process"] = r["progress"]
            r["size"] = int(r["ysfilesize"])
            r["format"]=r["openformat"]
        return raw_data
    
    def bt_task_check(self, url):
        r = self.session.get(self.QUERY_URL, params={
                             "callback": "queryUrl",
                             "u": url,
                             "random": self._random,
                             "tcache": self._now})
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        if len(args) < 12:
            return {}
        if not args[2]:
            return {}
        result = dict(
                      flag = args[0],
                      cid = args[1],
                      size = args[2],
                      title = title_fix(args[3]),
                      is_full = args[4],
                      random = args[11])
        filelist = []
        for subtitle, subformatsize, size, valid, file_icon, findex in zip(*args[5:11]):
            tmp_file = dict(
                            title = subtitle,
                            formatsize = subformatsize,
                            size=size,
                            file_icon = file_icon,
                            ext = "",
                            index = findex,
                            valid = int(valid),
                            )
            filelist.append(tmp_file)
        result['filelist'] = filelist
        return result
    
    def add_bt_task_with_dict(self, url, info):
        if not info: return False
        if info['flag'] == 0: return False
        data = dict(
                    uid = self.uid,
                    btname = info["title"],
                    cid = info["cid"],
                    goldbean = 0,
                    silverbean = 0,
                    tsize = info["size"],
                    findex = "_".join(_file['index'] for _file in info["filelist"] if _file["valid"]),
                    size = "_".join(_file['size'] for _file in info["filelist"] if _file["valid"]),
                    #name = "undefined",
                    o_taskid = 0,
                    o_page = "task",
                    class_id = 0)
        data["from"] = 0
        r = self.session.post(self.BT_TASK_COMMIT_URL, data)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        if "jsonp1234567890" in r.content:
            return True
        return False
    
    def add_bt_task(self, url, add_all=True, title=None):
        info = self.bt_task_check(url)
        if not info: return False
        if title is not None:
            info['title'] = title
        if add_all:
            for _file in info['filelist']:
                _file['valid'] = 1
        return self.add_bt_task_with_dict(url, info)
    
    def task_check(self, url):
        r = self.session.get(self.TASK_CHECK_URL, params={
                             "callback": "queryCid",
                             "url": url,
                             "random": self._random,
                             "tcache": self._now})
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        if len(args) < 8:
            return {}
        result = dict(
                      cid = args[0],
                      gcid = args[1],
                      size = args[2],
                      title = title_fix(args[4]),
                      goldbean_need = args[5],
                      silverbean_need = args[6],
                      is_full = args[7],
                      random = args[8])
        return result
    
    def add_task_with_dict(self, url, info):
        params = dict(
                      callback="ret_task",
                      uid=self.uid,
                      cid=info['cid'],
                      gcid=info['gcid'],
                      size=info['size'],
                      goldbean=0,
                      silverbean=0,
                      t=info['title'],
                      url=url,
                      type=0,
                      o_page="task",
                      o_taskid=0,
                      class_id=0,
                      database="undefined",
                      time="Wed May 30 2012 14:22:01 GMT 0800 (CST)",
                      noCacheIE=self._now)
        r = self.session.get(self.TASK_COMMIT_URL, params=params)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        if "ret_task" in r.content:
            return True
        return False
    
    def add_task(self, url, title=None):
        info = self.task_check(url)
        if not info: return False
        if title is not None:
            info['title'] = title
        return self.add_task_with_dict(url, info)
    
    def batch_task_check(self, url_list):
        data = dict(url="\r\n".join(url_list), random=self._random)
        r = self.session.post(self.BATCH_TASK_CHECK_URL, data=data)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        m = re.search("""(parent.begin_task_batch_resp.*?)</script>""",
                      r.content)
        assert m
        function, args = parser_js_function_call(m.group(1))
        DEBUG(pformat(args))
        assert args
        return args[0] if args else {}
    
    def add_batch_task_with_dict(self, info):
        data = dict(
                    batch_old_taskid=",".join([0, ]*len(info)),
                    batch_old_database=",".join([0, ]*len(info)),
                    class_id=0,
                    )
        data["cid[]"] = []
        data["url[]"] = []
        for i, task in enumerate(info):
            data["cid[]"].append(task.get("cid", ""))
            data["url[]"].append(task["url"])
        r = self.session.post(self.BATCH_TASK_COMMIT_URL, data=data)
        DEBUG(pformat(r.content))
        r.raise_for_status()
        if "jsonp1234567890" in r.content:
            return True
        return False
    
    def add_batch_task(self, url_list):
        # will fail of space limited
        info = self.batch_task_check(url_list)
        if not info: return False
        return self.add_batch_task_with_dict(info)
    
    def _torrent_upload(self, filename, fp):
        files = {'filepath': (filename, fp)}
        r = self.session.post(self.TORRENT_UPDATE_URL, data={"random": self._random}, files=files)
        DEBUG(pformat(r.content))
        r.raise_for_status()
        m = re.search("""btResult =(.*?);</script>""",
                      r.content)
        if not m:
            m = re.search(r"""(parent\.edit_bt_list.*?);\s*</script>""", r.content)
        if not m:
            return {}
        function, args = parser_js_function_call(m.group(1))
        DEBUG(pformat(args))
        assert args
        return args[0] if (args and args[0]['ret_value']) else {}
    
    def torrent_upload(self, filename, fp):
        info = self._torrent_upload(filename, fp)
        if not info: return {}
        result = dict(
                      flag = info['ret_value'],
                      cid = info['infoid'],
                      is_full = info['is_full'],
                      random = info.get('random', 0),
                      title = info['ftitle'],
                      size = info['btsize'],
                      )
        filelist = []
        for _file in info['filelist']:
            tmp_file = dict(
                            title = _file['subtitle'],
                            formatsize = _file['subformatsize'],
                            size = _file['subsize'],
                            file_icon = _file['file_icon'],
                            ext = _file['ext'],
                            index = _file['findex'],
                            valid = _file['valid'],
                            )
            filelist.append(tmp_file)
        result['filelist'] = filelist
        
        return result
    
    def torrent_upload_by_path(self, path):
        import os.path
        with open(path, "rb") as fp:
            return self.torrent_upload(os.path.split(path)[1], fp)
    
    def add_bt_task_by_path(self, path, add_all=True, title=None):
        path = path.strip()
        if not path.lower().endswith(".torrent"):
            return False
        info = self.torrent_upload_by_path(path)
        if not info: return False
        if title is not None:
            info['title'] = title
        if add_all:
            for _file in info['filelist']:
                _file['valid'] = 1
        return self.add_bt_task_with_dict("", info)
    
    def add(self, url, title=None):
        url_type = determin_url_type(url)
        if url_type in ("bt", "magnet"):
            return self.add_bt_task(url, title=title)
        elif url_type in ("normal", "ed2k", "thunder"):
            return self.add_task(url, title=title)
        elif url_type == "local_file":
            return self.add_bt_task_by_path(url[7:])
        else:
            return self.add_batch_task([url, ])
    
    def _get_bt_list(self, tid, cid):
        self.session.cookies["pagenum"] = str(2000)
        r = self.session.get(self.FILL_BT_LIST, params=dict(
                                                            callback="fill_bt_list",
                                                            tid = tid,
                                                            infoid = cid,
                                                            g_net = 1,
                                                            p = 1,
                                                            uid = self.uid,
                                                            noCacheIE = self._now))
        
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        if not args:
            return {}
        if isinstance(args[0], basestring):
            raise LiXianAPIException, args[0]
        return args[0].get("Result", {})
    
    def get_bt_list(self, tid, cid):
        raw_data = self._get_bt_list(tid, cid)
        assert cid == raw_data.get("Infoid")
        result = []
        for r in raw_data.get("Record", []):
            tmp = dict(
                       task_id=int(r['taskid']),
                       url=r['url'],
                       lixian_url=r['downurl'],
                       cid=r['cid'],
                       title=r['title'],
                       status=self.d_status.get(int(r['download_status'])),
                       dirtitle=r['dirtitle'],
                       process=r['percent'],
                       size=int(r['filesize']),
                       format=r['openformat'],
                       )
            result.append(tmp)
        return result
    
    def delay_task(self, task_ids):
        tmp_ids = [str(x)+"_1" for x in task_ids]
        r = self.session.get(self.TASK_DELAY_URL % dict(
                                                        ids = ",".join(tmp_ids),
                                                        cachetime = self._now))
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        if args and args[0].get("result") == 1:
            return True
        return False
    
    def task_delete(self, task_ids):
        jsonp = 'jsonp%s' % self._now
        data = {'taskids': task_ids+',', 'databases': '0,'}
        url = 'http://dynamic.cloud.vip.xunlei.com/interface/task_delete?callback=%s&type=%s&noCacheIE=%s' %(jsonp, 2, self._now)
        response = self.urlopen(url, data=data).read()
        response = remove_bom(response)
        assert_response(response, jsonp, '{"result":1,"type":2}')

    def task_pause(self, task_ids):
        r = self.session.get(self.TASK_PAUSE_URL, params = {
                             "tid": ",".join(map(str, task_ids)),
                             "uid": self.uid,
                             "noCacheIE": self._now
                             })
        r.raise_for_status()
        DEBUG(pformat(r.content))
        if "pause_task_resp" in r.content:
            return True
        return False

    def redownload(self, task_ids):
        r = self.session.post(self.REDOWNLOAD_URL, data = {
                              "id[]": task_ids,
                              "cid[]": ["",]*len(task_ids),
                              "url[]": ["",]*len(task_ids),
                              "taskname[]": ["",]*len(task_ids),
                              "download_status[]": [5,]*len(task_ids),
                              "type": 1,
                              })
        r.raise_for_status()
        DEBUG(pformat(r.content))
        if "jsonp1234567890(1)" in r.content:
            return True
        return False

    def get_wait_time(self, task_id, key=None):
        params = dict(
                      callback = "download_check_respo",
                      t = self._now,
                      taskid = task_id)
        if key:
            params["key"] = key
        r = self.session.get(self.GET_WAIT_TIME_URL, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0] if args else {}

    def get_free_url(self, nm_list=[], bt_list=[]):
        info = {}
        params = dict(
                      key=info.get("key", ""),
                      list=",".join((str(x) for x in nm_list+bt_list)),
                      nm_list=",".join((str(x) for x in nm_list)),
                      bt_list=",".join((str(x) for x in bt_list)),
                      uid=self.uid,
                      t=self._now)
        r = self.session.get(self.GET_FREE_URL, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0] if args else {}

    def get_task_process(self, nm_list=[], bt_list=[], with_summary=False):
        params = dict(
                      callback="rebuild",
                      list=",".join((str(x) for x in nm_list+bt_list)),
                      nm_list=",".join((str(x) for x in nm_list)),
                      bt_list=",".join((str(x) for x in bt_list)),
                      uid=self.uid,
                      noCacheIE=self._now,
                      )
        r = self.session.get(self.GET_TASK_PROCESS, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        args = args[0]
        
        result = []
        for task in args.get("Process", {}).get("Record", []) if args else []:
            status = None
            if task.get('fsize', u'0B') == u'0B':
                # it's a task own by other account
                status = 'failed'
            tmp = dict(
                       task_id = int(task['tid']),
                       cid = task.get('cid', None),
                       status = status or self.d_status.get(int(task['download_status']), "waiting"),
                       process = task['percent'],
                       leave_time = task['leave_time'],
                       speed = int(task['speed']),
                       lixian_url = task.get('lixian_url', None),
                       )
            result.append(tmp)
        if with_summary:
            return result, args.get("Process", {}).get("Task", {})
        else:
            return result

    def share(self, emails, tasks, msg="", task_list=None):
        if task_list is None:
            task_list = self.get_task_list()
        payload = []
        i = 0
        for task in task_list:
            if task["task_id"] in tasks:
                if task["task_type"] == "bt":
                    #TODO
                    pass
                else:
                    if not task["lixian_url"]: continue
                    url_params = parse_url(task['lixian_url'])
                    tmp = {
                        "cid_%d" % i : task["cid"],
                        "file_size_%d" % i : task["size"],
                        "gcid_%d" % i : url_params.get("g", ""),
                        "url_%d" % i : task["url"],
                        "title_%d" % i : task["taskname"],
                        "section_%d" % i : url_params.get("scn", "")}
                    i += 1
                    payload.append(tmp)
        data = dict(
                    uid = self.uid,
                    sessionid = self.get_cookie("sessionid"),
                    msg = msg,
                    resv_email = ";".join(emails),
                    data = json.dumps(payload))
        r = self.session.post(self.SHARE_URL, data)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        if args and args[0] == 1:
            return True
        return False

    def check_login(self):
        r = self.session.get(self.CHECK_LOGIN_URL)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        if args and args[0].get("result") == 1:
            self.uid = int(args[0]["data"].get("userid"))
            self.isvip = args[0]["data"].get("vipstate")
            self.nickname = args[0]["data"].get("nickname")
            self.username = args[0]["data"].get("usrname")
            self.task_url = self.TASK_URL % self.uid
            return True
        return False

    def get_cookie(self, attr=""):
        cookies = self.session.cookies
        if attr:
            return cookies[attr]
        return cookies
    
    def logout(self):
        sessionid = self.get_cookie("sessionid")
        if sessionid:
            self.session.get(self.LOGOUT_URL % {"sessionid": sessionid})
        self.session.cookies.clear()
        self.islogin = False
        self.task_url = None
    
    # functions for vod.lixian.xunlei.com
    
    def vod_redirect_play(self, url, fp=None):
        params = {
            "action": "http_sec",
            "location": "list",
            "from": "vlist",
            "go": "check",
            "furl": url,
        }
        if fp:
            files = {'filepath': (url, fp)}
        else:
            files = None
        r = self.session.post(self.VOD_REDIRECT_PLAY_URL, params=params, files=files)
        r.raise_for_status()
        DEBUG(pformat(r.content))
        m = re.search("""top.location.href="(.*?)";""",
                      r.content)
        assert m
        return m.group(1)

    def vod_get_play_url(self, url, bindex=-1):
        params = {
            "callback": "jsonp1234567890",
            "t": self._now,
            "check": 0,
            "url": url,
            "format": 225536,  #225536:g, 282880:p
            "bindex": bindex,
            "isipad": 0,
        }
        r = self.session.get(self.VOD_GET_PLAY_URL, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0]
    
    def cloud_play_get_url(self, url):
        params = {
            "url": url,
            "platform": 1,
            "userid": self.session.cookies["userid"],
            "jsonp": "jsonp1234567890",
            "sessionid": self.session.cookies['sessionid'],
        }
        r = self.session.get(self.CLOUD_PLAY_GET_URL, params=params)
        print r.content
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        assert args
        return args[0]
    
    def vod_check_vip(self):
        pass
    
    def vod_get_bt_list(self, cid):
        pass
    
    def vod_get_list_pic(self, gcids):
        params = {
            "callback": "jsonp1234567890",
            "t": self._now,
            "ids": "", # urlhash
            "gcid": ",".join(gcids),
            "rate": 0
        }
        r = self.session.get(self.VOD_GET_LIST_PIC, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0]
    
    def vod_get_bt_pic(self, cid, bindex=[]):
        """
            get gcid and shotcut of movice of bt task
            * max length of bindex is 18
            """
        params = {
            "jsonp" : "jsonp1234567890",
            "t" : self._now,
            "info_hash" : cid,
            "req_list" : "/".join(map(str, bindex)),
        }
        r = self.session.get(self.VOD_GET_BT_PIC % params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0].get("resp", {})
    
    def vod_get_process(self, url_list):
        params = {
            "callback": "jsonp1234567890",
            "t": self._now,
            "url_list": "####".join(url_list),
            "id_list": "####".join(["list_bt_%d" % x for x in range(len(url_list))]),
            "palform": 0,
        }
        r = self.session.get(self.VOD_GET_PROCESS, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0]
    
    # functions for kuai.xunlei.com
    
    def webfilemail_url_analysis(self, url):
        params = {
            "action": "webfilemail_url_analysis",
            "url": url,
            "cachetime": self._now,
        }
        r = self.session.get(self.WEBFILEMAIL_INTERFACE_URL, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0]
    
    def is_miaoxia(self, url, bindex=[]):
        if bindex:
            bindex = sample(bindex, 15) if len(bindex) > 15 else bindex
            ret = self.vod_get_bt_pic(url, bindex)
            if not ret.get("screenshot_list"):
                return False
            for each in ret["screenshot_list"]:
                if not each.get("gcid"):
                    return False
            return True
        else:
            info = self.webfilemail_url_analysis(url)
            if info['result'] == '0':
                return True
            return False
    
    def get_vip_info(self):
        params = {
            "cachetime": self._now,
            "callback": "jsonp1234567890"
        }
        r = self.session.get(self.VIP_INFO_URL, params=params)
        r.raise_for_status()
        function, args = parser_js_function_call(r.content)
        DEBUG(pformat(args))
        assert args
        return args[0]
