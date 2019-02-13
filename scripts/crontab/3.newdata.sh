#!/bin/bash


cd /opt/tools/report/
cp report.cfg.tpl report.cfg
sed -i 's/^processors=.*/processors=batchprocessing,genstdanslib,comparer/' report.cfg
sed -i 's/^flush_tbl_std_ans=.*/flush_tbl_std_ans=0/' report.cfg
sed -i 's#^corpus=.*#corpus=input/unsolved_query.xlsx#' report.cfg

source venv/bin/activate
python run.py --op workflow

cd scripts
python genunsolvedcorpus.py

cd /opt/tools/report/
sed -i 's/^processors=.*/processors=batchprocessingunsolvedquery,gentblunsolvedquery/' report.cfg
python run.py --op workflow
