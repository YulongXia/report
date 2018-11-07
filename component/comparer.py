# encoding: utf-8

import time
import os
import pandas as pd
import json

from data_management.databroker.databroker import databroker
from . import abstract

class comparer(abstract.abstract):
    def __init__(self,**kwargs):
        self.comparer = kwargs["comparer"]
        self.output_file_basic_statistic = os.path.join(kwargs["output_dir_basic_statistic"],"{}-{}-{}.xlsx".format("basic",kwargs["project"],time.strftime('%Y-%m-%d-%H_%M_%S',time.localtime(time.time()))))
        self.ComparerDict = {"default":self.compare_default}

    def process(self,info): 
        func = self.getComparer(self.comparer)
        c1 = json.loads(info.get("batchprocessing",""))
        c2 = info.get("genstdanslib","")
        result = func(c1,c2)
        return result
    
    def getComparer(self,label):
        return self.ComparerDict.get(label)
    
    def compare_default(self,c1,c2):
        if c1 == "" or c2 == "" or len(c1) == 0 or len(c2) == 0:
            return 0
        data = {"query":[],"inStdAns":[],"compare":[]}
        for ele in c1:
            d = c2.get(ele["query"],None)
            data["query"].append(ele["query"])
            if d is not None:
                data["inStdAns"].append(1)
                ele["inStdAns"] = 1
                if len(d["result"]) == 0 or d["result"] == "Null":
                    if [ e["value"] for e in ele["tags"] if e["key_name"] == "entity" ][0] == d["entity"] and [ e["value"] for e in ele["tags"] if e["key_name"] == "intent" ][0] == d["intent"]:
                        data["compare"].append(1)
                        ele["compare"] = 1
                    else:
                        data["compare"].append(0)
                        ele["compare"] = 0
                else:
                    if [ e["value"] for e in ele["tags"] if e["key_name"] == "result" ][0] == d["result"]:
                        data["compare"].append(1)
                        ele["compare"] = 1
                    else:
                        data["compare"].append(0)
                        ele["compare"] = 0
            else:
                ele["inStdAns"] = 0
                ele["compare"] = ""
                data["inStdAns"].append(0)
                data["compare"].append("")
        grouped = self.statistic(data,["inStdAns","compare"])
        return c1
    
    def statistic(self,data,groupby_keys):
        df = pd.DataFrame(data)
        grouped = df.groupby(groupby_keys)
        count = grouped.agg(["count"])
        count.to_excel(self.output_file_basic_statistic)
        return grouped
        

