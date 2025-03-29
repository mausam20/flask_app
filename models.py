from datetime import date, timedelta,datetime
from flask import current_app,g
import time
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import logging
import numpy as np


class BquerySession():
    def __init__(self, config_data):
        credentials = service_account.Credentials.from_service_account_file(config_data.get("service_account_json"))
        project_id = config_data.get("project_id")
        self.client = bigquery.Client(credentials= credentials,project=project_id)
        self.bquery_table_id = config_data.get("table_id")
        self.hrs_table = config_data.get("hrs_table")
        
    #filter={'time':{'start_time':<timestamp>,'end_time':<timestamp>}}
    def create_query(self,table_name, config_data, glid, columns = [], filters= {}):
        columns_str = "*"
        if columns:
            columns.extend(["GLID","event_date"])
            columns_str = ",".join(columns)
        where_str= "GLID = %s"%glid
        
        if filters:
            start_data = filters.get('time').get('start_time')
            end_date = filters.get('time').get('end_time')
            if not isinstance(start_data,str):
                start_data = datetime.strftime(filters.get('time').get('start_time'),"%Y-%m-%d")
            if not isinstance(end_date,str):
                end_date = datetime.strftime(filters.get('time').get('end_time'),"%Y-%m-%d")
            where_str = "%s and event_date between '%s' and '%s'"%(where_str, start_data,end_date)
        query_str = "select %s from %s where %s "%(columns_str,table_name,where_str)
        g.query = query_str
        return query_str
    
    def read_table(self, config_data, glid, columns = [], filters= {}):
        start = time.perf_counter()
        table_name = self.bquery_table_id
        query_str = self.create_query(table_name, config_data, glid, columns.copy(), filters)
        query_job = self.client.query(query_str)
        results = query_job.result()
        results = [dict(data) for data in results]
        query_time = time.perf_counter() - start
        g.query_time = query_time
        return results
    

    def get_last_year_count(self,glid,columns,config_data,par_func):
        start = time.perf_counter()
        current_date =date.today()
        filters = {'time':{'start_time':current_date-timedelta(days=365),'end_time':current_date}}
        count_df = self.read_table(config_data, glid, columns.copy(),filters)
        count_df = pd.DataFrame(count_df)
        if count_df.empty:
            return None
        if par_func=="aggregate":
            agg_df = count_df[columns].sum()
        elif par_func=="risk_score":
            hrs_value = count_df.loc[0,"latest_hrs_tag"] if count_df.loc[0,"latest_hrs_tag"] else 0
            bi_trigger_count = count_df.loc[0,"bi_trigger_count"]
            count_df["month"] = pd.to_datetime(count_df.event_date,format="%Y-%m-%d").dt.month
            month_columns = columns + ["month"]
            month_count_df = count_df[month_columns].groupby("month").sum()
            month_count_df["activation_ticket"] = np.where(month_count_df["activation_ticket"]>0,1,0)
            agg_df = month_count_df[columns].sum()
            agg_df["latest_hrs_tag"],agg_df["bi_trigger_count"] = hrs_value,bi_trigger_count
        agg_data = agg_df.to_dict()
        resp_time = time.perf_counter()-start
        g.count_func_time = resp_time
        return agg_data
