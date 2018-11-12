# encoding: utf-8

import time
import os
import MySQLdb
import MySQLdb.cursors

from data_management.databroker.databroker import databroker
from data_management.accessdb.accessRDB import accessRDB
from . import abstract

class genstdanslib(abstract.abstract):
    tpl_correct_corpus_ids = {"taixingxiao":"""select distinct(corpus_id) from tbl_tag_taixingxiao where (desc_id like "taixingxiao.2.%" or desc_id like "taixingxiao.5.%")and corpus_id not in (select distinct(corpus_id) from ((select distinct(corpus_id) from tbl_tag_taixingxiao where desc_id = "taixingxiao.2.22" and key_id = (select id from tbl_key where key_name = "处理情况") and value = '未标注') union (select distinct(corpus_id) from tbl_tag_taixingxiao where desc_id like "taixingxiao.5.%" and key_id = (select id from tbl_key where key_name = "hual_解决状态") and value not in ('已解决','1.0','1_推荐','推荐_1','1'))) as a)"""}

    tpl_latest_tag = {"taixingxiao":"""select b.key_name,a.value from tbl_tag_taixingxiao as a ,tbl_key as b where (a.desc_id like "taixingxiao.2.%" or a.desc_id like "taixingxiao.5.%") and b.key_name in ("{tag}") and a.key_id = b.id and a.corpus_id = {corpus_id} order by a.time desc limit 1"""}

    tpl_query = """select query from tbl_corpus where id = {corpus_id}"""

    tpl_insert_std_ans = """insert into {tbl} (key_name,value,query,time) value ("{key_name}","{value}","{query}","{time}")"""

    tpl_truncate_std_ans = """truncate table tbl_std_ans"""

    tpl_query_std_ans = """select * from tbl_std_ans"""

    def __init__(self,**kwargs):
        self.flush_flag = kwargs["flush_tbl_std_ans"]
        self.tags = kwargs["tags"]
        self.project = kwargs["project"]
        self.host = kwargs["dbhost"]
        self.port = int(kwargs["dbport"])
        self.db = kwargs["dbname"]
        self.tbl_std_ans = kwargs["tbl_std_ans"]
        self.user = kwargs["dbuser"]
        self.passwd = kwargs["dbpasswd"]
        self.charset = "utf8"
        self.cursorclass = MySQLdb.cursors.DictCursor
        self.tags_stdlib_basic = kwargs["tags_stdlib_basic"]

        self.conn = MySQLdb.connect(host=self.host,port=self.port,db=self.db,user=self.user,passwd=self.passwd,charset=self.charset,cursorclass=self.cursorclass)
        self.cursor = self.conn.cursor()

    def process(self,info):
        if not self.flush_flag:
            result = self.getDataFromStdAns()
            info[self.__class__.__name__] = result
            return result
        else:
            self.cursor.execute(self.tpl_truncate_std_ans)
        a = accessRDB()
        # { 
        #   query1:{tag1:val1,tag2:val2,...,tagN:valN},
        #   query2:{tag1:val1,tag2:val2,...,tagN:valN},
        #   ...
        # }
        result = dict()
        # ({corpus_id:xxx},{corpus_id:yyy},...)
        result_corpus_ids = a.execute(stmt=self.tpl_correct_corpus_ids[self.project])
        cur_time = time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
        for res in result_corpus_ids:
            key,value = list(res.items())[0]
            query = a.execute(stmt=self.tpl_query.format(corpus_id=value))[0]["query"]
            result[query] = dict()
            tags = []
            tags.extend(self.tags)
            tags.extend(self.tags_stdlib_basic)
            
            for tag in tags:
                tag_value = a.execute(stmt=self.tpl_latest_tag[self.project].format(tag="{}".format(tag),corpus_id=value))
                if len(tag_value) == 0 or len(tag_value[0]["value"]) == 0 :
                    result[query][tag] = "Null"
                else:
                    result[query][tag] = tag_value[0]["value"]
                self.execute(stmt=self.tpl_insert_std_ans.format(tbl=self.tbl_std_ans,key_name=tag,value=result[query][tag].replace('"','\"'),query=query,time=cur_time))
        info[self.__class__.__name__] = result
        return result

    def getDataFromStdAns(self):
        # { 
        #   query1:{tag1:val1,tag2:val2,...,tagN:valN},
        #   query2:{tag1:val1,tag2:val2,...,tagN:valN},
        #   ...
        # }
        result = dict()
        all_data = self.execute(stmt=self.tpl_query_std_ans)
        for data in all_data:
            if data["query"] not in result:
                result[data["query"]] = {data["key_name"]:data["value"]}
            else:
                result[data["query"]][data["key_name"]] = data["value"]
        return result
    
    def execute(self,**kwargs):
        self.cursor.execute(kwargs["stmt"])
        self.conn.commit()
        result = self.cursor.fetchall()
        return result

        
        

