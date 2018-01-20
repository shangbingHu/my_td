__author__ = 'Ice'

import re
import urllib
import httplib2
import random
import cStringIO
import time
from gzip import GzipFile


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance

class Http(Singleton):
    print "========= Init ========"
    http = httplib2.Http()

class Web(object):
    @staticmethod
    def do_get(url, headers=None):
        response = None
        content = None
        retry_time = 0
        http = httplib2.Http()
        while(True):
            try:
                if retry_time > 5:
                    raise Exception("bad server or network")
                response, content = http.request(url, "GET", headers=headers)
                break
            except Exception, e:
                time.sleep(120)
                retry_time += 1
                print "Error: %s" % str(e)
                print "retry for %s time" % retry_time
            finally:
                pass
        return response, content.decode('gbk').encode('utf-8')

    @staticmethod
    def do_post(url, headers=None, data={}):
        response = None
        content = None
        retry_time = 0
        http = httplib2.Http()
        while(True):
            try:
                if retry_time > 5:
                    raise Exception("bad server or network")
                response, content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(data))
                break
            except Exception, e:
                time.sleep(120)
                retry_time += 1
                print "Error: %s" % str(e)
                print "retry for %s time" % retry_time
            finally:
                pass
        #print response
        return response, content.decode('gbk').encode('utf-8')


    @staticmethod
    def get_cookie(response, ismultiple=False):
        print response
        try:
            cookie_temp = response["set-cookie"]
        except:
            pass
            return None
        # if there are more than one "set-cookie" segment
        # all of them will be joined by ,
        # A known issue is that the expire attribute with ","
        if ismultiple:
            cookie = cookie_temp.replace(",", ";")
        else:
            print "try to get cookie"
            cookie_temp = cookie_temp.replace(" path=/;", "")
            cookie_temp = cookie_temp.replace(" path=/", "")
            cookie_temp = cookie_temp.replace(" httponly", "")
            cookie_temp = re.sub(r"expires=\w+,\s\w+-\w+-\w+\s\d+:\d+:\d+\sGMT;", "", cookie_temp)
            cookie_temp = re.sub(r"\s*,\s*", "", cookie_temp)
            cookie = cookie_temp
        return cookie


class StrUtils(object):
    @staticmethod
    def search(given_str, pattern, index=1):
        match = re.search(pattern, given_str)
        if match:
            return match.group(index)
        return None

    @staticmethod
    def getstrgroup(given_str, pattern):
        regex = re.compile(pattern)
        match = regex.search(given_str)
        if match:
            return match.groups()
        return None

    @staticmethod
    def strtoint(str):
        return int(str)

    @staticmethod
    def getrandomstr():
        return str(random.uniform(0.00000000000000001, 0.99999999999999999))


class CodingUtils(object):
    @staticmethod
    def decodegzip(gzipcontent):
        try:
            gf = GzipFile(fileobj=cStringIO.StringIO(gzipcontent), mode="rb")
            html_data = gf.read()
        except:
            print "gzip error"
            html_data = gf.extrabuf
        return html_data


class Utils(object):
    @staticmethod
    def between(num, start, end):
        if num > start and num < end:
            return True
        return False

class TimeUtils(object):
    WEEK_MAP = {
        "Mon": 1,
        "Tue": 2,
        "Wed": 3,
        "Thu": 4,
        "Fri": 5,
        "Sat": 6,
        "Sun": 7
    }
    @staticmethod
    def getweekandhourfromtime(time):
        """here, time should be GMT time format"""
        # "Wed, 27 Nov 2013 04:12:50 GMT3"
        week, hour = StrUtils.getstrgroup(time, "(\w+),.*(\d+):\d+:\d+")
        week = TimeUtils.WEEK_MAP[week]
        hour = int(hour) + 8
        return week, hour

    @staticmethod
    def getcurrenttime():
        tm = time.localtime()
        return time.strftime("%Y-%m-%d %H:%M:%S", tm)