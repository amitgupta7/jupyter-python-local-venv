#!/usr/bin/env python
# coding: utf-8

# ## load data
# * `root`: location of the csv files.
# * `fromDt` and `toDt` are start and end dates for range

# In[1]:


import sys
sys.path.append('../')

import dataframeLoader as dfl
import pandas as pd

from importlib import reload 
reload(dfl)

# Provide csv data location and appliance and timerange information.
root = '../../.dataDir'
fromDt = '2024-11-10'
toDt = '2024-12-10'

# Provide list of prometheus metrics to load. 
# metricsArr = ['cpu_used', 'download_workers_count', 'memory_used', 'task_queue_length', 'infra_access_latency', 'pod_cpu_usage', 'pod_memory_usage'] 
metricsArr = ['cpu_used'
              ,'task_queue_length'
              , 'memory_used'
              ]


daterange=[fromDt, toDt]
df = dfl.loadApplianceTimeSeriesData(root, metricsArr, daterange)


# In[2]:


display(df)
print(df.metrics.unique())


# ## Generate plotly report
# * `appliance_id`: unique identifier of the appliance.

# In[3]:


reload(dfl)
appliance_id='58e98e10-1b19-4c84-93c0-db2ad5903b80'
fromDate = '2024-11-26'
toDate = '2024-11-29'
dfp = df[(df['appliance_id'] == appliance_id) & (df['ts'].between(fromDate, toDate))]
# Get Full list of metrics in dataframe
# print(dfp.metrics.unique())
# Provide metrics to show from the data frame. Order is preserved.
metrics_category_order = {# "Indicator": "Chart Description"
            "task_queue_length_avg":  "Average temporary task queue length (indicator of file tasks in queue for download / scanning)"
            ,"cpu_used_avg": "Average CPU by Appliance Node/VM"
            , "memory_used_avg": "Average Memory by Appliance Node/VM"
            ,"uniqPodCount": "Scheduled Download workers by datasource"
            , "fileDownloadTimeInHrs":  "Time spent by connectors in downloading files for scanning"
            , "IdleTimeInHrs": "Cumulative idle-time spent waiting by (all) download workers by datasource"
            , "scanTimeInHrs":  "Cumulative time spent scanning by (all) download workers by datasource"
            , "dataScannedinGB" :  "Data scanned in Gigabits per hour"
            ,"numberOfColsScanned":  "Number of structured data columns scanned per hour"
            , "numberOfChunksScanned":  "Number of structured data row chunks (of 64 rows) scanned per hour"
            , "numFilesScanned":  "Number of files/tables scanned per hour"
            , "avgFileSizeInMB":  "Average size of file or table-data scanned"
             }

title = 'Hourly appliance plot for appliance_id '+appliance_id
fig  = dfl.plotMetricsFacetForApplianceId(dfp, title, metrics_category_order)
fig.show()

