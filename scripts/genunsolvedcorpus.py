# encoding: utf-8

import MySQLdb
import pandas as pd
host="127.0.0.1"
port=3306
user="xiayulong"
passwd="xiayulong"
db="data_management"
conn=MySQLdb.connect(host=host,port=port,db=db,user=user,passwd=passwd,charset="utf8")
cursor=conn.cursor()

unsolved_queries_sql="""select query from tbl_corpus where id not in (select distinct(id) from (select distinct(corpus_id) as id from tbl_tag_taixingxiao where desc_id in (select concat("taixingxiao.",task_id,".",batch_id) from tbl_batch where task_id in (select id from tbl_task where status = 2)) union select distinct(corpus_id) as id from tbl_tag_taixingxiao where desc_id in (select concat("taixingxiao.",task_id,".",batch_id) from tbl_batch where task_id in (select id from tbl_task where status = 1)) and key_id = (select id from tbl_key where key_name = "hual_解决状态") and value in ('已解决','1.0','1_推荐','推荐_1','1')) as t )"""

cursor.execute(unsolved_queries_sql)
unsolved_queries=[ row[0] for row in cursor.fetchall() ]
df=pd.DataFrame({"query":unsolved_queries})
df.to_excel("../../input/unsolved_query.xlsx",index=False)


