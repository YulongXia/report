#! /bin/bash

cd /opt/tools/report
source venv/bin/activate
while read line
do
    corpus=`echo $line|grep -Po '(?<=corpus=)[^[:space:]]+'`
    sequencemode=`echo $line|grep -Po '(?<=sequencemode=)[^[:space:]]+'`
    cp report.cfg.tpl report.cfg
    sed -i "s#^corpus=.*#corpus=input/$corpus#" report.cfg
    sed -i "s#^sequencemode=.*#sequencemode=$sequencemode#" report.cfg
    sed -i "s#^processors=.*#processors=batchprocessing,genstdanslib,comparer#" report.cfg
    sed -i "s#^flush_tbl_std_ans=.*#flush_tbl_std_ans=0#" report.cfg
    echo $corpus $sequencemode
    python run.py --op workflow
done < scripts/crontab/playbook.cfg
