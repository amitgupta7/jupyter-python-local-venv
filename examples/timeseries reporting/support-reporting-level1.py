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
dfp = df[(df['ts'].between(fromDate, toDate))]
fig  = dfl.plotMetricsFacetForApplianceId(dfp, appliance_id)
fig.show()

