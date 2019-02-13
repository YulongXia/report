# encoding: utf-8

import time
import os

from data_management.databroker.databroker import databroker
from . import batchprocessing

class batchprocessingunsolvedquery(batchprocessing.batchprocessing):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.tags = kwargs["tags_unsolved_query"]
        self.url = self.url_tpl.format(host=self.host,port=self.port,bot=self.bot)
        self.corpus = kwargs["corpus_unsolved_query"]
