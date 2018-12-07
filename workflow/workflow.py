# encoding: utf-8
import codecs
import os
import importlib

class workflow(object):
    list_options = ["processors","tags_unsolved_query","tags_stdlib_basic"]
    bool_options = ["flush_tbl_std_ans"]
    bool_value = ("t","true","1")
    def __init__(self,filename,conf=None):
        if conf is None:
            self.conf = self.parse_conf(filename)
        else:
            self.conf = conf
        self.processors = []
        for processor in self.conf["processors"]:
            module = importlib.import_module('report.component.{}'.format(processor))
            processor_obj = getattr(module,processor)(**self.conf)
            self.processors.append(processor_obj)

    @classmethod
    def parse_conf(cls,filename):
        conf = dict()
        with codecs.open(filename,"r",encoding="utf-8") as fd_conf:
            for line in fd_conf.readlines():
                line = line.strip()
                if line.startswith("#") or len(line) == 0:
                    continue
                
                split_idx = line.find("=")
                if split_idx == 0 or split_idx == len(line) - 1:
                    raise Exception("invalid attribute in {}".format(line))
                
                attribute = line[:split_idx]
                value = line[split_idx+1:]
                if attribute.endswith("_tags"):
                    if "tags" not in conf:
                        conf["tags"] = [ val.strip() for val in value.split(",") if len(val.strip()) != 0 ]
                    else:
                        for val in value.split(","):
                            val = val.strip()
                            if len(val) != 0 and val not in conf["tags"]:
                                conf["tags"].append(val)
                else:
                    conf[attribute] = [ val.strip() for val in value.split(",") if len(val.strip()) != 0 ]
                    if len(conf[attribute]) == 1 and attribute not in cls.list_options:
                        conf[attribute] = conf[attribute][0]
                        if attribute in cls.bool_options:
                            if conf[attribute].lower() not in cls.bool_value:
                                conf[attribute] = False
                            else:
                                conf[attribute] = True
        return conf

    def run(self):
        info = dict()
        for processor in self.processors:
            processor.process(info)


