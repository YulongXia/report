# system pre-define
default_tags=result,intermediate_intent,intermediate_pquery,intermediate_entities,intermediate_properties
tbl_std_ans=tbl_std_ans
tbl_unsolved_query=tbl_unsolved_query
tags_unsolved_query=result
tags_stdlib_basic=标准答案,hual_标准答案,intermediate_intent,intermediate_pquery,intermediate_entities,intermediate_properties

# user define
customized_tags=result
host=115.182.62.171
port=1781
bot=taikang_txx_all
project=taixingxiao
corpus_unsolved_query=input/unsolved_query.xlsx
# modify
# corpus=input/20181212/(none-dup)问题数据1130-1202-已校对 1(1).xlsx
corpus=input/20190212/none-dup-问题数据1231-190101-已校对-2019-02-12-11_13_59.xlsx
#corpus=input/20190114/all_correct_queries.xlsx
#processors=genstdanslib,
processors=batchprocessing,genstdanslib,comparer
dbhost=127.0.0.1
dbport=3306
dbuser=xiayulong
dbpasswd=xiayulong
dbname=data_management
flush_tbl_std_ans=0
sequencemode=1
comparer=default
# file is named what consists of "basic"(string,prefix),the value of project and time("suffix") e.g. basic-taixingxiao-2018-11-06-16-22-00.xlsx
output_dir_basic_statistic=output/statistic/
# file is named what consists of "assistant"(string,prefix),the value of project and time("suffix") e.g. assistant-taixingxiao-2018-11-06-16-22-00.xlsx
output_dir_assistant_file=output/assistant/
