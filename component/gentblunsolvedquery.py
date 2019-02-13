# encoding: utf-8

import time
import os
import MySQLdb
import MySQLdb.cursors
import json

from data_management.databroker.databroker import databroker
from data_management.accessdb.accessRDB import accessRDB
from . import genstdanslib

class gentblunsolvedquery(genstdanslib.genstdanslib):
    tpl_insert_unsloved_query = """insert into {tbl} (key_name,value,corpus_id,query,time) values ("{key_name}","{value}",{corpus_id},"{query}","{time}") """
    tpl_corpus_id = """select id from tbl_corpus where query = "{query}" """
    tpl_truncate_unsolved_query = """truncate table tbl_unsolved_query"""
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.tbl_unsolved_query = kwargs["tbl_unsolved_query"]
        self.tags_unsolved_query = kwargs["tags_unsolved_query"]
    
    def process(self,info):
        self.cursor.execute(self.tpl_truncate_unsolved_query)
        data = json.loads(info["batchprocessingunsolvedquery"])
        a = accessRDB()
        cur_time = time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
        for ele in data:
            query = ele["query"]
            #if query == '?' or len(query.strip()) == 0:
            #    continue
            for tag in ele["tags"]:
                if tag["key"] in self.tags_unsolved_query:
                    corpus_id = a.execute(stmt=self.tpl_corpus_id.format(query=query))[0]["id"]
                    tag["value"] = tag["value"].replace('"','\\"')
                    query = query.replace('"','\\"')
                    self.execute(stmt=self.tpl_insert_unsloved_query.format(tbl=self.tbl_unsolved_query,key_name=tag["key"],value=tag["value"],corpus_id=corpus_id,query=query,time=cur_time))
        return 
    
    def execute(self,**kwargs):
        self.cursor.execute(kwargs["stmt"])
        self.conn.commit()
        result = self.cursor.fetchall()
        return result
