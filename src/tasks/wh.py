#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging.handlers
import urllib2
from datetime import *
from urllib import quote

from BeautifulSoup import BeautifulSoup

from src.dao.sqlite_utils import *

reload(sys)
sys.setdefaultencoding("utf-8")

#init logger
LOG_FILE = 'wh_area_spider.log'  
  
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler   
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'  
  
formatter = logging.Formatter(fmt)      # 实例化formatter  
handler.setFormatter(formatter)         # 为handler添加formatter  
  
logger = logging.getLogger('wh_area_spider')    # 获取名为tst的logger  
logger.addHandler(handler)                      # 为logger添加handler  
logger.setLevel(logging.DEBUG) 

# hierarchy
class HHtmlParser():
    def __init__(self, curr_date, sqlite):
        self.sqlite = sqlite
        #area field need to do urlencode
        self.host = "http://119.97.201.28:8087/"
        self.area_data_url_pattern = "http://119.97.201.28:8087/xmqk.asp?page=%d&domain=%s&blname=&bladdr=&prname="
        #n_house is normal house, c_house is commerial house
        self.table_index = ["project_name", "total_n_house", "selled_n_house", "can_sell_n_house", "selled_c_house", "can_sell_c_house"]
        self.area_id = 0
        self.domain = ""
        self.response = ""
        self.area_page_parsed = False
        self.area_total_project_num = 0
        self.area_project_page_num = 0
        self.parse_date = curr_date
    
    def uencode(self, str):
        return quote(str.decode("utf-8").encode("gbk"))
    
    def parse_project_list_page(self, page_num, domain_encode):
        area_root_url = self.area_data_url_pattern % (page_num, domain_encode)
        try:
            self.response = urllib2.urlopen(area_root_url)
        except urllib2.URLError, e:
            logger.error("domain: %s url: %s error reason: %s" % (self.domain, area_root_url, e.reason))
        
        html_content = ''.join(self.response)
        
        #sys_type = sys.getfilesystemencoding()
        #info_code = chardet.detect(html_content).get('encoding','utf-8')
        #info_code = "GB2312"
        #html_content = html_content.decode(info_code,'ignore').encode(sys_type)
        html_content = html_content.decode("gb2312",'ignore').encode("utf-8")
        
        soup = BeautifulSoup(html_content)
        
        if self.area_page_parsed == False:
            #parse total project in current area
            page_num_obj = soup.findAll("font", {"color":"#FF0000"})
            if len(page_num_obj) != 5:
                logger.error("分析%s内楼盘列表翻页信息失败，格式不对")
                exit(-1)
            total_project_num = int(page_num_obj[1].string)
            total_page_num = int(page_num_obj[3].string)
            logger.debug("area %s project info(%d:%d)" % (self.domain, total_project_num, total_page_num))
            
            self.area_project_page_num = total_page_num
            self.area_total_project_num = total_project_num
            self.area_page_parsed = True
        
        #parse project list
        project_list = soup.findAll("tr", {"bgcolor":"#FFFFFF"})
        logger.debug("area %s page: %d project list num: %d" % (self.domain, page_num, len(project_list)))
        
        index = 0
        project_info_list = []
        for proj_tr in project_list:
            index += 1
            proj_info = {"name":"", "url":"", "total":0, "h_selled":0, "h_sell":0, "c_selled":0, "c_sell" : 0}
            #td tag
            proj = proj_tr.findAll("td")
            if len(proj) != 6:
                logger.error("area %s page: %d project index: %d format invalid" % (self.domain, page_num, index))
                exit(1)
            #name url
            proj_info["name"] = proj[0].contents[1].contents[0].string.strip()
            proj_info["url"] = quote(proj[0].contents[1]["href"].encode("gbk")).replace("%3F", "?").replace("%3D", "=")
            proj_info["total"] = self.parse_num(proj[1].string.strip())
            proj_info["h_selled"] = self.parse_num(proj[2].string.strip())
            proj_info["h_sell"] = self.parse_num(proj[3].string.strip())
            proj_info["c_selled"] = self.parse_num(proj[4].string.strip())
            proj_info["c_sell"] = self.parse_num(proj[5].string.strip())
            
            project_info_list.append(proj_info)
        
        return [self.area_project_page_num, project_info_list]
        
    def parse_project_info(self, project_name, url):
        project_info_url = "%s%s" % (self.host, url)
        project_info_page = ""
        try:
            project_info_page = urllib2.urlopen(project_info_url)
        except urllib2.URLError, e:
            logger.error("domain: %s project: %s url: %s error reason: %s" % (self.domain, project_name, project_info_url, e.reason))
            return None
        
        html_content = ''.join(project_info_page)
        
        #sys_type = sys.getfilesystemencoding()
        #info_code = chardet.detect(html_content).get('encoding','utf-8')
        #info_code = "GB2312"
        #html_content = html_content.decode(info_code,'ignore').encode(sys_type)
        
        html_content = html_content.decode("gb2312",'ignore').encode("utf-8")
        
        soup = BeautifulSoup(html_content)
        #project build sell detail info page url
        detail_trs = soup.findAll("tr", {"bgcolor": "#FFFFFF"})
        if(len(detail_trs) == 0):
            print "parse_project_info(): NOT FOUND."
            return None;

        #detail info tr
        build_url = ""
        build_url_tag = soup.findAll("font", {"color": "red"})
        if len(build_url_tag) == 0:
            build_url = quote(build_url_tag[0].a["href"].encode("gbk")).replace("%3F", "?").replace("%3D", "=")
        #project address
        proj_addr = detail_trs[1].findAll("td")[1].string.strip()
        #project time
        proj_times = detail_trs[2].findAll("td")
        proj_begin = proj_times[1].string.strip()
        proj_finish = proj_times[3].string.strip()
        
        proj_times = detail_trs[7].findAll("td")
        proj_sell_time = proj_times[1].string.strip()
        
        #project land area size
        proj_land_area = detail_trs[3].findAll("td")[2].string.strip().split(" ")[0]
        
        #project build area size
        proj_build = detail_trs[5].findAll("td")
        proj_build_area = proj_build[1].string.strip().split(" ")[0]
        proj_people_rate = proj_build[3].string.strip()
        
        #project build num
        proj_build = detail_trs[6].findAll("td")
        proj_house_num = proj_build[1].string.strip().split(" ")[0]
        proj_build_num = self.sub_digit(proj_build[3].string.strip())
        
        return {"project_addr": proj_addr,
                "project_begin_date": self.format_date(proj_begin),
                "project_finish_date": self.format_date(proj_finish),
                "project_sell_date": self.format_date(proj_sell_time),
                "project_land_area": self.parse_num_1(proj_land_area),
                "project_build_area": self.parse_num_1(proj_build_area),
                "project_people_rate": self.parse_num_1(proj_people_rate),
                "project_build_num": self.parse_num_1(proj_build_num),
                "project_house_num": self.parse_num_1(proj_house_num),
                "project_build_url": build_url}
    
    def parse_num(self, str_value):
        str_ret = ""
        for c in str_value.strip():
            if c.isdigit() or c == '-':
                str_ret += c
        
        if str_ret == "-" or str_ret == "":
            str_ret = "0"
        
        return str_ret
    
    def parse_num_1(self, str_value):
        str_ret = ""
        for c in str_value.strip():
            if c.isdigit() or c == '.' or c == '-':
                str_ret += c
            else:
                break
        
        if str_ret == "-" or str_ret == "":
            str_ret = "0"
        
        return str_ret
    
    def format_date(self, str_date):
        try:
            f = str_date.strip().split("-")
            if len(f) != 3:
                logger.error("date string invalid: %s" % str_date)
                return str_date
            else:
                str_ret = f[0]
                str_ret += "-%02d-" % int(f[1])
                str_ret += "%02d" % int(f[2])
                return str_ret
        except Exception, e:
            print str_date, e
            return ""
    
    def sub_digit(self, str_value):
        str_ret = ""
        for c in str_value:
            if c.isdigit():
                str_ret += c
            else:
                break
        
        return str_ret
    
    def parse(self, domain, area_id):
        self.area_id = area_id
        self.domain = domain
        domain_encode = self.uencode(domain)
        page_index = 1
        page_total = 1
        while page_index <= page_total:
            [page_total, page_info_list] = self.parse_project_list_page(page_index, domain_encode)
            page_index += 1
        
            tuple_index = 0
            for item in page_info_list:
                [existed, project_id] = self.sqlite.check_project_info_existed(item["name"])
                if not existed:
                    proj_info = self.parse_project_info(item["name"], item["url"])
                    if proj_info:
                        project_id = self.sqlite.insert_project_info(self.area_id, self.domain, item["name"], proj_info)
                    else:
                        project_id = -1
                [existed, tmp_id] = self.sqlite.check_project_sell_info(project_id)
                if not existed:
                    self.sqlite.insert_project_sell_info(project_id, item)
                tuple_index += 1
                print "%s-%d-%d : %s" % (domain, page_index - 1, tuple_index, item)
        self.sqlite.insert_area_project_num(self.area_id, self.area_total_project_num)


wh_area = [[1,"江汉区"],
           [2, "江岸区"],
           [3,"硚口区"],
           [4,"汉阳区"],
           [5,"武昌区"],
           [6,"洪山区"],
           [7,"青山区"],
           [8,"黄陂区"],
           [9,"东西湖区"],
           [10,"东湖新技术开发区"],
           [11,"东湖风景区"],
           [12,"武汉经济开发区"],
           [13,"江夏区"],
           [14,"蔡甸区"],
           [15,"汉南区"],
           [16,"新洲区"]]

if __name__ == '__main__':
    update_hour = 0
    while True:
        cur_datetime = datetime.today()
        if abs(cur_datetime.hour - update_hour) < 6:
            time.sleep(30*60)
            continue
        update_hour = cur_datetime.hour
        curr_date = cur_datetime.strftime('%Y-%m-%d')
        logger.info("Begin crawl wh_house data date:  %s" % curr_date)
        sqlite = Sqlite3Utils(curr_date, logger)
        hhp = HHtmlParser(curr_date, sqlite)
        for area in wh_area:
            hhp.parse(area[1], area[0])
        sqlite.close()
