# encoding: utf-8

import time
import os
import json

from data_management.databroker.databroker import databroker
from data_management.accessdb.accessRDB import accessRDB
from . import abstract

class batchprocessing(abstract.abstract):
    url_tpl = 'http://{host}:{port}/bot/{bot}/simulator'
    sql_raw_corpus = {"taixingxiao":"""select corpus_id,desc_id,sn from tbl_tag_taixingxiao where desc_id like "taixingxiao.%.1" group by corpus_id,desc_id,sn """}
    tpl_corpus_id = """select id from tbl_corpus where query = "{}"  """
    tpl_corpus_time = {"taixingxiao":""" select time from tbl_tag_taixingxiao where corpus_id = "{corpus_id}" and desc_id = "{desc_id}" and sn = "{sn}" limit 1"""}
    def __init__(self,**kwargs):
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.bot = kwargs["bot"]
        self.corpus = kwargs["corpus"]
        self.tags = kwargs["tags"]
        self.url = self.url_tpl.format(host=self.host,port=self.port,bot=self.bot)
        self.project = kwargs["project"]

    def process(self,info): 
        d = databroker(*self.tags,url=self.url,corpus=self.corpus)
        desc_id = "batchprocessing-" + time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
        result_json = d.Standardize(desc_id,output=None)
        data = json.loads(result_json)
        a = accessRDB()
        rows = a.execute(stmt=self.sql_raw_corpus[self.project])
        raw_corpus = dict()
        for row in rows:
            if row["corpus_id"] in raw_corpus:
                row["corpus_id"].append({ key:value for x in row for key,value in x.items() })
            else:
                row["corpus_id"] = [ { key:value for x in row for key,value in x.items() } ]
        for ele in data:
            ele["extra_tags"] = dict()
            ele["extra_tags"]["times"] = 0
            ele["extra_tags"]["appearences"] = ""
            res = a.execute(stmt=self.tpl_corpus_id.format(ele["query"]))
            if len(res) == 0:
                continue
            corpus_id = res[0]["id"]
            search = raw_corpus.get(corpus_id,None)
            if search is None:
                continue
            appearences = []
            for obj in search:
                res = a.execute(stmt=self.tpl_corpus_time[self.project].format(**obj))
                appearences.append(res[0]["time"])
            ele["extra_tags"]["times"] = len(appearences)
            ele["extra_tags"]["appearences"] = "\n".join(appearences)
           
        info[self.__class__.__name__] = result_json    
        return result_json
        

