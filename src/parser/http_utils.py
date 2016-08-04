import urllib2,cookielib
import time
import json


def download(url, count=1, charset="gb18030"):
    try:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        response = opener.open(url, timeout=5)
        html = ''.join(response)
        html = html.decode(charset).encode("utf-8")
        return html
    except Exception, e:
        print count, url, e
        if count < 5:
            time.sleep(3)
            return download(url, count + 1)
        else:
            return None
    return None


def get_binary_file(url, f):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib2.urlopen(req)
        img_file = open(f, 'wb')
        img_file.write(response.read())
        img_file.close()
    except Exception, e:
        print url, e
        img_file.close()


def get_json(url):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib2.urlopen(req)
        return json.loads(response.read())
    except Exception, e:
        print url, e
        return None