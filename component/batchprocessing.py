# encoding: utf-8

import time
import os

from data_management.databroker.databroker import databroker
from . import abstract

class batchprocessing(abstract.abstract):
    url_tpl = 'http://{host}:{port}/bot/{bot}/simulator'
    def __init__(self,**kwargs):
        self.host = kwargs["host"]
        self.port = kwargs["port"]
        self.bot = kwargs["bot"]
        self.corpus = kwargs["corpus"]
        self.tags = kwargs["tags"]
        self.url = self.url_tpl.format(host=self.host,port=self.port,bot=self.bot)

    def process(self,info): 
        d = databroker(*self.tags,url=self.url,corpus=self.corpus)
        desc_id = "batchprocessing-" + time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
        result_json = d.Standardize(desc_id,output="std_json/{time}.json".format(time=time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))))
        info[self.__class__.__name__] = result_json
        return result_json
        

