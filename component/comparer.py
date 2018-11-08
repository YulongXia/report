# encoding: utf-8

import time
import os
import pandas as pd
import json
import codecs

from data_management.databroker.databroker import databroker
from data_management.accessdb.accessRDB import accessRDB
from report.component.gentblunsolvedquery import gentblunsolvedquery
from . import abstract

class comparer(abstract.abstract):
    def __init__(self,**kwargs):
        self.comparer = kwargs["comparer"]
        cur_time = time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))
        self.output_file_basic_statistic = os.path.join(kwargs["output_dir_basic_statistic"],"{}-{}-{}.xlsx".format("basic",kwargs["project"],cur_time))
        self.output_dir_assitant_file = os.path.join(kwargs["output_dir_assitant_file"],"{}-{}-{}.xlsx".format("assitant",kwargs["project"],cur_time))
        self.ComparerDict = {"default":self.compare_default}
        self.cursor = gentblunsolvedquery(**kwargs)

    def process(self,info): 
        func = self.getComparer(self.comparer)
        c1 = json.loads(info.get("batchprocessing",""))
        c2 = info.get("genstdanslib","")
        result = func(c1,c2)
        info[self.__class__.__name__] = result
        self.to_excel(result,self.output_dir_assitant_file)
        return result
    
    def to_excel(self,data,output):
        tags = ["query"]
        tags.extend([tag["key"] for tag in data[0]["tags"]])
        tags.extend([key for key in data[0]["extra_tags"].keys()])
        result = []
        for d in data:
            row = []
            row.append(d["query"])
            for tag in d["tags"]:
                row.append(tag["value"])
            for key,value in d["extra_tags"].items():
                row.append(value)
            result.append(row)
        df = pd.DataFrame(result,columns=tags)
        df.to_excel(output,index=False)

    def getComparer(self,label):
        return self.ComparerDict.get(label)
    
    def compare_default(self,c1,c2):
        if c1 == "" or c2 == "" or len(c1) == 0 or len(c2) == 0:
            return 0
        data = {"query":[],"inStdAns":[],"compare":[]}
        for ele in c1:
            d = c2.get(ele["query"],None)
            data["query"].append(ele["query"])
            ele["extra_tags"] = dict()
            ele["extra_tags"]["sim_query"] = ""
            ele["extra_tags"]["inStdAns"] = 0
            ele["extra_tags"]["compare"] = ""
            if d is not None:
                data["inStdAns"].append(1)
                ele["extra_tags"]["inStdAns"] = 1
                if len(d["result"]) == 0 or d["result"] == "Null":
                    if [ e["value"] for e in ele["tags"] if e["key"] == "entity" ][0] == d["entity"] and [ e["value"] for e in ele["tags"] if e["key"] == "intent" ][0] == d["intent"]:
                        data["compare"].append(1)
                        ele["extra_tags"]["compare"] = 1
                    else:
                        data["compare"].append(0)
                        ele["extra_tags"]["compare"] = 0
                else:
                    if [ e["value"] for e in ele["tags"] if e["key"] == "result" ][0] == d["result"]:
                        data["compare"].append(1)
                        ele["extra_tags"]["compare"] = 1
                    else:
                        data["compare"].append(0)
                        ele["extra_tags"]["compare"] = 0
            else:
                data["inStdAns"].append(0)
                data["compare"].append("")
                ele["extra_tags"]["sim_query"] = self.get_extra_info_from_unsolved_query_set("pquery",ele)
        self.statistic(data,["inStdAns","compare"])
        return c1
    
    def statistic(self,data,groupby_keys):
        df = pd.DataFrame(data)
        grouped = df.groupby(groupby_keys)
        count = grouped.agg(["count"])
        count.to_excel(self.output_file_basic_statistic)
        return grouped
    
    def get_extra_info_from_unsolved_query_set(self,tag,data):
        tpl_aggregate = """select value,group_concat(corpus_id) as corpus_ids from tbl_unsolved_query where key_name = "{tag}" group by value"""
        ret = "Null"
        a = accessRDB()
        result = self.cursor.execute(stmt=tpl_aggregate.format(tag=tag))
        target = [ t for t in data["tags"] if t["key"] == tag ]
        if len(target) == 0:
            return ret
        for res in result:
            if res["value"] == target[0]["value"]:                    
                tmp = [ row["query"] for row in a.execute(stmt="""select query from tbl_corpus where id in ({ids})""".format(ids=res["corpus_ids"])) ]
                ret = "\n---\n".join(tmp)
        return ret



