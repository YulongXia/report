# encoding: utf-8

import time
import os
import pandas as pd
import json
import codecs
import re

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
        self.ComparerDict = {"default":self.comparer_default}
        self.cursor = gentblunsolvedquery(**kwargs)
        self.tags_stdlib_basic = kwargs["tags_stdlib_basic"]

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

    
    def comparer_default(self,datafrombot,datafromstdlib):
        """
        params:
        1. datafrombot: format like the followings
                [
                    {"query":...,tags:[
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    ...
                                    ]},
                    {"query":...,tags:[
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    ...
                                    ]},
                ]
        
        2. datafromstdlib: format like the followings
                { 
                    query1:{tag1:val1,tag2:val2,...,tagN:valN},
                    query2:{tag1:val1,tag2:val2,...,tagN:valN},
                    ...
                }
        return:
                [
                    {"query":...,tags:[
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    ...
                                    ]
                                ,extra_tags: {key1:value1,key2:value2}
                    },
                    {"query":...,tags:[
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    {"key":...,"value":...,"desc_id":...,"time":...},
                                    ...
                                    ]
                                ,extra_tags: {key1:value1,key2:value2}
                    },
                ]
                
        """
        if datafrombot == "" or datafromstdlib == "" or len(datafrombot) == 0 or len(datafromstdlib) == 0:
            return 0
        basic_statistic_data = {"query":[],"inStdAns":[],"compare":[]}
        for ele in datafrombot:
            basic_statistic_data["query"].append(ele["query"])
            ele["extra_tags"] = dict()
            ele["extra_tags"]["sim_query"] = ""
            ele["extra_tags"]["inStdAns"] = 0
            ele["extra_tags"]["compare"] = ""

            inStd = datafromstdlib.get(ele["query"],None)
            if inStd is not None:
                basic_statistic_data["inStdAns"].append(1)
                ele["extra_tags"]["inStdAns"] = 1
                if self.isSame(ele,inStd):
                    basic_statistic_data["compare"].append(1)
                    ele["extra_tags"]["compare"] = 1
                else:
                    basic_statistic_data["compare"].append(0)
                    ele["extra_tags"]["compare"] = 0
            else:
                basic_statistic_data["inStdAns"].append(0)
                basic_statistic_data["compare"].append("")
                #ele["extra_tags"]["sim_query"] = self.get_extra_info_from_unsolved_query_set("pquery",ele)
        self.statistic(basic_statistic_data,["inStdAns","compare"])
        return datafrombot

    def isSame(self,eleinbot,eleinstd):
        stdans_label = ["标准答案","hual_标准答案"]
        intermediate = [ ans_type for ans_type in self.tags_stdlib_basic if ans_type not in stdans_label ]
        for ans_type in self.tags_stdlib_basic:
            if eleinstd[ans_type] != "Null" and ans_type in stdans_label:
                # s1: realtime answer
                # s2: correct answer
                s1 = ""
                for tag in eleinbot["tags"]:
                    if tag["key"] == "result":
                        s1 = tag["value"]
                        break
                if len(s1) == 0:
                    return False
                s2 = eleinstd[ans_type].strip()
                s1 = self.regularization(s1)
                s2 = self.regularization(s2)
                word1 = s1[:400]
                word2 = s2[:400]
                record = [[-1 for i in range(len(word1) + 1)] for j in range(len(word2) + 1)]
                ed = self.MinEditingDistance(len(word1)-1,len(word2)-1,word1,word2,record)
                if ed/(len(word1)+1) < 0.1:
                    return True
                if s2 in s1:
                    return True
            elif ans_type in intermediate:
                tag_value = ""
                for tag in eleinbot["tags"]:
                    if tag["key"] == ans_type:
                        tag_value = tag["value"]
                        break
                if tag_value != eleinstd[ans_type].strip():
                    return False
        if len(intermediate) != 0:
            return True    
        return False
    
    def compare_test(self,c1,c2):
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
                #ele["extra_tags"]["sim_query"] = self.get_extra_info_from_unsolved_query_set("pquery",ele)
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
    

    def MinEditingDistance(self,xi,yi,X,Y,record):
        """
        src : X
        dst : Y
        """
        if record[yi+1][xi+1] >= 0:
            return record[yi+1][xi+1]
        if xi < 0:
            record[yi+1][xi+1] = yi + 1
            return yi + 1
        if yi < 0:
            record[yi+1][xi+1] = xi + 1
            return xi + 1
        # 增
        a = self.MinEditingDistance(xi,yi-1,X,Y,record) + 1
        # 删
        b = self.MinEditingDistance(xi-1,yi,X,Y,record) + 1
        # 改
        c = self.MinEditingDistance(xi-1,yi-1,X,Y,record) + 1
        if X[xi] == Y[yi]:
            d = self.MinEditingDistance(xi-1,yi-1,X,Y,record)
            record[yi+1][xi+1] = min(a,b,c,d)
            return record[yi+1][xi+1]
        else:
            record[yi+1][xi+1] = min(a,b,c)
            return record[yi+1][xi+1]



    def regularization(self,t):
        t = re.sub(r"<br>",r"\n",t)
        t = re.sub(r"^[^：:]+[：:]",r"",t)
        t = re.sub(r"<img src='(\S+)'/>",r"\g<1>",t)
        t = re.sub(r"<[^>]+>",r"",t)
        # t = re.sub(r"[\s\u0020-\u007f\u2000-\u206f\u3000-\u303f\uff00-\uffef\uf075]+","",t)
        t = re.sub(r"[\s\.\!\/_,$%^*()?;；:\-【】\"\'\[\]——！，;:。？、~@#￥%……&*（）]+","",t)
        t = re.sub(r".+您可能关注以下问题.+",r"",t)
        return t
