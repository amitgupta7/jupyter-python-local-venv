#!/usr/bin/env python
# coding: utf-8

# ## Provided as-is (w/o support)
# Kubernetes clusters collect various application and infrastrcuture statistics. While this information is useful, it's very difficult to identify which metrics are useful for monitoring and troubleshooting. The Goal here is to collect this information, and use a statistical model to identify which metrics should be included in reports/dashboard such that:
# * Unnecessary overhead and sensory overload can be reduced.
# * Time can be saved by prioritising monitoring the correct metrics.
# 
# This process needs to assume `zero knowlidge` of the workings of the cluster, workload being run and any other information. This way, `generic` clusters can be monitored without explicitly programming dashboards based on internal knowlidge. This is also a good method to discover/verify  application knowlidge/bottlenecks with statistical data analyis. 
# 
# ## Step1: Data Loading 
# We will load cpu, memory, task_queue information along with stats from strcutured and unstrucutred scans from csv files stored on disk using the `dataframeLoader` helper.
# ```python
# # The dataframeLoader helper function implements the loadApplianceTimeSeriesData method.
# # This method loads the csv files, and pivots them to generate distinct "metrics" timeseries. 
# # see https://github.com/amitgupta7/docker-jupy-ntbk-s3-reporting/blob/main/dataframeLoader.py
# ``` 

# In[1]:


import sys
sys.path.append('../')

import dataframeLoader as dfl
import pandas as pd
from importlib import reload 
reload(dfl)

# Provide csv data location and appliance and timerange information.
root = '../../.dataDir'
fromDt = '2024-06-01'
toDt = '2024-11-01'

# Provide list of prometheus metrics to load. 
metricsArr = ['cpu_used', 'download_workers_count', 'memory_used', 'task_queue_length', 'infra_access_latency', 'pod_cpu_usage', 'pod_memory_usage'] 
# metricsArr = ['cpu_used'
#               ,'task_queue_length'
#               , 'memory_used'
#               ]

daterange=[fromDt, toDt]
df = dfl.loadApplianceTimeSeriesData(root, metricsArr, daterange)


# ## Step2: Data Pivoting
# We now aggregate the data by `appliance_id` (unique identifier for our cluster) and `ts` timestamp, to get different metrics values as separate columns. Notice there are:
# * Statistical significance (consider correlation for appliances with atleast 30 non-zero scan time values, ie the appliance should be scanning for atleast 30 hours before considering it statistically significant).
#     * 200+ appliances
#     * Total scanning time of over 15 years!!
# 
# * 33 metrics -> 22 metrics
#     * Decide between `max` or `avg` values if both are present. 
#     * We chose to display `avg` values metrics in this case after some trial and error.
#         * Except for memory (where max indicates spikes/oom conditions better) 
# 
# * Tracked every hour

# In[2]:


#consider only appliances with a certain number of scanning intervals.
min_scanning_intervals = 10
dfp = df.pivot_table(index=['appliance_id','ts'], columns=['metrics'], values='value', aggfunc='sum').reset_index()
max_list = list(dfp.filter(regex='max'))
# maxlist = ['cpu_used_max', 'linkerq_max', 'memory_used_avg', 'taskq_max', 'tmp_taskq_max']
# we would like to use max memory (to indicate spikes/oom conditions)
max_list = list(map(lambda x: x.replace('memory_used_max', 'memory_used_avg'), max_list))
print('cols removed', max_list)
dfp = dfp[dfp.columns.drop(max_list)]
stat_sig = dfp.fillna(0).groupby(['appliance_id']).scanTime.agg(lambda x: x.ne(0).sum())
stat_sig = stat_sig[stat_sig > min_scanning_intervals].sort_values(ascending=False)
print('cols retained', dfp.columns)
print(len(stat_sig), 'statistically significant appliances with total scan time of', stat_sig.sum()/24/365, 'years')
dfp = dfp[dfp.appliance_id.isin(stat_sig.index)]

display(dfp)


# ## Step 3: Data transformation and correlation
# We need to acheve two main goals:
# 1. Isolate data for individual appliance.
# 2. Remove ghost correlation between unrelated metrics.
#     * We will calculate percentage change between adjacent timeseries values.
# 3. Calculate absolute correlation between metrics for each single appliance.
#     * Transpose every `metrics` corelation.
# 4. Generate correlation for every `appliance_id` and `metric` identifier using steps 1, 2 and 3
# 

# In[3]:


# appliance = '01c75278-9c0d-41be-b693-c970b18dbedc'
# for metric in metrics_category_order:
dfc_arr = []
for pod in dfp.appliance_id.unique():
    dfa = dfp[(dfp.appliance_id == pod)]
    dfa = dfa.drop(['appliance_id', 'ts'], axis=1)
    dfa = dfa.pct_change(periods=1, fill_method=None)
    dfca = dfa.corr().abs()
    # print(type(dfca))
    for col in dfca.columns:
        # print(col)
        dfc = dfca[col].to_frame().T
        dfc.insert(0, 'metric', col )
        dfc.insert(0, 'appliance_id', pod )
        dfc_arr.append(dfc)
dfc = pd.concat(dfc_arr, ignore_index=True)
dfc.set_index('appliance_id', inplace=True)
dfc.head()


# ## Step 4: Isolate related metrics using correlation
# We now iterate over each `metric`, to see if there is any significant statistical correlation to be found across `appliance_id`s. This is done with two steps:
# 
# 1. Removing outliers:
#     * Remove any metrics with `3rd quantile correlation value below the cut-off`. This cut-off can be varied for depending on use cases:
#         * 0.9 for Exec Dashboards
#         * 0.8 for Customer Ops
#         * 0.7 for L1 - support
#         * 0.6 for L2 - suport 
# 
# Please note that we are filtering metrics with `3rd quantile` correlation below the `moderate cut-off`. This ensures that atleast 25% of the values are correlated to reduce outliers.
# 
# 2. Plot box chart to visually represent metrics with any correlation (for cutoff as 0.3).  
# 
# 3. The network graph indicates specific correlation edges between metrics.
# 
# ## Final List of metrics 
# The below table shows the list of `metrics` that are useful with respective correlation `cutoff`. The cut-off values can be interpreted as follows:
# 
# * below 0.3     negligible correlation
# * 0.3 to 0.5    Low positive (negative) correlation
# * 0.5 to 0.7    Moderate positive (negative) correlation
# * 0.7 to 0.9    High positive (negative) correlation
# * 0.9 to 0.1    Very High positive (negative) correlation
# 

# In[4]:


import gravis as gv
import itertools
import networkx as nx
from IPython.display import Image

corr_vals = [0.6, 0.7, 0.8, 0.9]
mtrx_arr = []
graph_arr = []
for cutoff in corr_vals:
    arr = []
    for metr in dfc.metric.unique():
        dfcm = dfc[(dfc.metric == metr)]
        dfcm = dfcm.drop('metric', axis=1)
        dfcm = dfcm.drop(metr, axis=1)
        dfcm = dfcm.dropna(axis = 0, how = 'all')
        dfcm = dfcm.loc[:, dfcm.quantile(q=0.75) > cutoff]
        for x in dfcm.columns:
            arr.append(x)
            graph_arr.append((metr, x))
        if(cutoff == corr_vals[0]):
            if len(dfcm.columns) > 0:
                title=f'''Absolute correlation vs percent-change of {metr}
                (For median correlation greater than {cutoff})
                '''
                dfcm.plot(kind='box',vert=False,title=title,colormap='tab20')
    arr = list(set(arr))
    arr.insert(0,cutoff)
    mtrx_arr.append(arr)

display(pd.DataFrame(list(map(list, itertools.zip_longest(*mtrx_arr, fillvalue="")))))

g = nx.DiGraph()
g.add_edges_from(graph_arr)
fig = gv.d3(g
       , graph_height=800
       , use_node_size_normalization=True
       , zoom_factor=2
       , node_size_normalization_max=30
      ,use_edge_size_normalization=True
      ,use_collision_force=True
      ,node_label_size_factor=0.8
       , layout_algorithm_active=True
       )
fig.export_jpg('graph2.jpg', overwrite=True)
print("Correlation graph between appliance metrics")
Image('graph2.jpg')
# fig.display()

