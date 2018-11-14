# encoding: utf-8
import codecs
import os
import importlib
import argparse
import pandas as pd
from report.workflow.workflow import workflow
from report.component.batchprocessingunsolvedquery import batchprocessingunsolvedquery
from report.component.gentblunsolvedquery import gentblunsolvedquery
from report.component.comparer import comparer
from data_management.accessdb.accessRDB import accessRDB

def gen_corpus(data,output):
    result = {"query":[ele["query"] for ele in data]}
    df = pd.DataFrame(result)
    df.to_excel(output,index=False)
    return result

def statistic(in_xlsx,out_xlsx,groupby_keys="inStdAns,hual_解决状态"):
    df = pd.read_excel(in_xlsx)
    grouped = df.groupby(groupby_keys.split(","))
    count = grouped[df.columns[0]].agg(["count"])
    count.to_excel(out_xlsx)
    return grouped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run.py")
    parser.add_argument("--op")
    parser.add_argument("--input")
    parser.add_argument("--output")
    args = parser.parse_args()
    op = args.op
    if op == "workflow":
        wf = workflow(os.path.join(".","report.cfg"))
        wf.run()
    elif op == "gen-tbl-unsolved-query":
        conf = workflow.parse_conf(os.path.join(".","report.cfg"))
        conf["corpus"] = "input/unsolved_query.xlsx"
        a = accessRDB()
        result = a.execute(stmt="""select query from tbl_corpus where id in (select distinct(corpus_id) from ((select distinct(corpus_id) from tbl_tag_taixingxiao where desc_id = "taixingxiao.2.22" and key_id = (select id from tbl_key where key_name = "处理情况") and value = '未标注') union (select distinct(corpus_id) from tbl_tag_taixingxiao where desc_id like "taixingxiao.5.%" and key_id = (select id from tbl_key where key_name = "hual_解决状态") and value not in ('已解决','1.0','1_推荐','推荐_1','1'))) as a)""")
        gen_corpus(result,conf["corpus"])
        info = dict()
        processors = [batchprocessingunsolvedquery(**conf),gentblunsolvedquery(**conf)]
        for processor in processors:
            processor.process(info)
    elif op == "statistic":
        in_xlsx = args.input
        out_xlsx = args.output
        statistic(in_xlsx,out_xlsx)
