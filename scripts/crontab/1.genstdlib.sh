#!/bin/bash


cd /opt/tools/report/
cp report.cfg.tpl report.cfg
sed -i 's/^processors=.*/processors=genstdanslib,/' report.cfg
sed -i 's/^flush_std_ans=.*/flush_tbl_std_ans=1/' report.cfg

source venv/bin/activate
python run.py --op workflow
