## Load Dataframe
import pandas as pd
import plotly.express as px
from dateutil.parser import parse
import datetime as dt
import warnings
import fnmatch
import os
# Example
# import dataframeLoader as dfl
# dfl.loadDataFrameFromFileRegex('dataDir', 'securiti_appliance_cpu_used-max*.csv', metrics='cpu-max')
pd.set_option('future.no_silent_downcasting', True)

def loadPrometheusData(root, fileRegex, metricsName, fileAggFunc, fileExtn, aggfunction, **kwargs):
    daterange = kwargs.get('daterange', None)
    print("processing "+fileRegex+metricsName+'-'+fileAggFunc+'*'+fileExtn)
    df1 = loadDataFrameFromFileRegex(root, fileRegex+metricsName+'-'+fileAggFunc+'*'+fileExtn, metrics=metricsName+'_'+fileAggFunc, daterange=daterange)
    df1['metrics'] = metricsName+'_'+fileAggFunc
    # if(metricsName == 'task_queue_length'):
    #     df1.loc[df1['metrics_name'].str.contains('securiti-appliance-downloader-tasks-queue', regex=False), 'metrics'] = 'taskq_'+fileAggFunc
    #     df1.loc[df1['metrics_name'].str.contains('t-appliance-downloader-tasks-queue', regex=False), 'metrics'] = 'tmp_taskq_'+fileAggFunc
    #     df1.loc[df1['metrics_name'].str.contains('securiti-appliance-linker', regex=False), 'metrics'] = 'linkerq_'+fileAggFunc

    # if(metricsName == 'infra_access_latency'):
    #     df1.loc[df1['metrics_name'].str.contains('appliance_es_access_latency', regex=False), 'metrics'] = 'esLatency_'+fileAggFunc
    #     df1.loc[df1['metrics_name'].str.contains('appliance_postgres_access_latency', regex=False), 'metrics'] = 'pgLatency_'+fileAggFunc
    #     df1.loc[df1['metrics_name'].str.contains('appliance_redis_access_latency', regex=False), 'metrics'] = 'redisLatency_'+fileAggFunc

    df1['node_ip']=df1['node_ip'].fillna("master")
    df1 = df1.groupby(['appliance_id','ts', 'node_ip', 'metrics']).agg(value=('value', aggfunction)).reset_index()   
    df1['ts']=pd.to_datetime(df1['ts'],unit='s')
    return df1[['appliance_id','ts', 'node_ip', 'metrics', 'value']] 

def loadDataFrameFromFileRegex(root, regex, **kwargs):
    metrics = kwargs.get('metrics', None)
    daterange = kwargs.get('daterange', None)
    df_arr = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, regex) and os.path.getsize(os.path.join(path, name)) > 0:
                if checkDateRangeFromFileName(daterange, name):
                    # print(os.path.join(path, name))
                    df = pd.read_csv(os.path.join(path, name))
                    df.insert(1, 'metrics', metrics)
                    df_arr.append(df)
    if not df_arr:
        warnings.warn("No matching file found in "+root+" for regex: "+regex+". Empty dataframe will be returned." )
        return pd.DataFrame()    
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)      
        return pd.concat(df_arr, ignore_index=True)

def checkDateRangeFromFileName(daterange, name):
    if not daterange:
        return True    
    start_timestamp = parse(daterange[0],fuzzy=True)
    end_timestamp = parse(daterange[1],fuzzy=True)
    if start_timestamp <= parse(name,fuzzy=True) <= end_timestamp: 
        return True
    return False
    
def plotMetricsFacetForApplianceId(dfp, ttl, cat_order, colorCol,ledgend):
    # dfp = fill_timeseries_zero_values(dfp)
    dfp = dfp[(dfp['metrics'].isin(cat_order))].drop_duplicates()
    cat_order_list = list(cat_order.keys())
    cat_order_overlap = sorted(set(cat_order_list).intersection(dfp.metrics.unique()),key=lambda x:cat_order_list.index(x))
    dfp.rename(columns={colorCol:ledgend}, inplace=True)
    fig = px.bar(dfp, 
                 x='ts', 
                 y="value", 
                 color=ledgend,
                 pattern_shape=ledgend,
                 facet_col='metrics', 
                 facet_col_wrap=1,
                 height=dfp['metrics'].unique().size*200, 
                 facet_row_spacing=0.02, 
                #  text_auto=True,
                 text_auto='.1f',
                 color_discrete_sequence=px.colors.qualitative.Alphabet, 
                 category_orders={"metrics": cat_order_overlap}, 
                 title=ttl
                 )
    fig.update_yaxes(matches=None)
    fig.update_traces(width=60*60*1000)
    fig.for_each_annotation(lambda a: a.update(text=updateCategoryLable(a.text, cat_order)))
    fromdt = dfp['ts'].min().date()
    todt=dfp['ts'].max().date()
    if todt > fromdt:
        fig.update_layout(xaxis=dict(
            rangeselector=dict(
                font = dict( color = "black"),
                buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(step="all")
            ])),
            rangeslider=dict(
                visible=True,
                thickness=0.01
                ),
                type="date", 
                range=[dfp['ts'].min(), dfp['ts'].min() + dt.timedelta(days=1)]
                )
            )
    fig = fig.update_yaxes(side='left', showticklabels=True, title='')
    fig.update_layout(plot_bgcolor="black", font_color='white', paper_bgcolor='black')
    return fig

def updateCategoryLable(txt, cat_order):
    txt = txt.split("=")[-1]
    return cat_order[txt]


def fill_timeseries_zero_values(dfp):
    dfp = dfp.pivot_table(index=['appliance_id','ts'], columns=['node_ip', 'metrics'], values='value', aggfunc='max').reset_index()
    dfp = dfp.drop('appliance_id', axis=1, level=0)
    dfp = dfp.set_index(['ts'])
    dfp = dfp.reindex(pd.date_range(dfp.index[0], dfp.index[-1], freq='h')).fillna(0)
    dfp.reset_index(level=[])
    dfp = pd.melt(dfp, ignore_index = False)
    return dfp

def loadStrucDataFromFileRegex(root, regex, **kwargs):
    daterange = kwargs.get('daterange', None)
    print("loading Strctured Data from file: "+regex)
    df9 = loadDataFrameFromFileRegex(root, regex, metrics='strcutured_Scan', daterange=daterange)
    df9.rename(columns={'pod':'appliance_id'}, inplace=True)
    cols = ['ds', 'dsid']
    df9['node_ip'] = df9[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    # df9.rename(columns={'ds':'node_ip'}, inplace=True)
    df9=df9.groupby(['appliance_id', 'ts', 'node_ip']).agg(\
    numFilesScanned=('numberOfTablesScanned', 'sum'), \
    numberOfColsScanned=('numberOfColsScanned', 'sum'), \
    uniqPodCount=('uniqPodCount', 'max'), \
    scanTimeInHrs=('processingTimeinHrs', 'sum'), \
    IdleTimeInHrs=('IdleTimeInHrs', 'sum'), \
    numberOfChunksScanned=('numberOfChunksScanned', 'max')).reset_index()
    df9['ts']=pd.to_datetime(df9['ts'],unit='ms')
    df9 = pd.melt(df9, id_vars=['appliance_id','ts', 'node_ip'], var_name='metrics', value_name='value').drop_duplicates()
    return df9

def loadConnectorDataFromFileRegex(root, regex, **kwargs):
    daterange = kwargs.get('daterange', None)
    print("loading Unstrctured Data from file: "+regex)
    df7 = loadDataFrameFromFileRegex(root, 'STRUCTURED-*.csv', metrics='strcu', daterange=daterange)
    df6 = loadDataFrameFromFileRegex(root, 'UNSTRUCTURED-*.csv', metrics='strcu', daterange=daterange)
    df6 = df6[['pod', 'dsid', 'ds']].drop_duplicates()
    df7 = df7[['pod', 'dsid', 'ds']].drop_duplicates()
    df7 = pd.concat([df6, df7], ignore_index=True).drop_duplicates()
    df8 = loadDataFrameFromFileRegex(root, 'SCANPROC-*.csv', metrics='scan_proc', daterange=daterange)
    df8.rename(columns={'datasource_id':'dsid'}, inplace=True)
    dfsp=pd.merge(df8, df7, on=['dsid', 'pod'], how='left')
    cols = ['ds', 'dsid']
    dfsp['node_ip'] = dfsp[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    dfsp.rename(columns={'pod':'appliance_id'}, inplace=True)
    dfsp = dfsp.groupby(['appliance_id', 'ts', 'node_ip']).agg(
    fileDownloadTimeInHrs=('downloadTimeInHrs', 'sum')).reset_index()
    dfsp['ts']=pd.to_datetime(dfsp['ts'],unit='ms')
    dfsp = pd.melt(dfsp, id_vars=['appliance_id','ts', 'node_ip'], var_name='metrics', value_name='value').drop_duplicates()
    return dfsp

def loadUnstrucDataFromFileRegex(root, regex, **kwargs):
    daterange = kwargs.get('daterange', None)
    print("loading Unstrctured Data from file: "+regex)
    df9 = loadDataFrameFromFileRegex(root, regex, metrics='unStrcutured_Scan', daterange=daterange)
    df9.rename(columns={'pod':'appliance_id'}, inplace=True)
    cols = ['ds', 'dsid']
    df9['node_ip'] = df9[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    # df9.rename(columns={'ds':'node_ip'}, inplace=True)
    df9=df9.groupby(['appliance_id', 'ts', 'node_ip']).agg(\
    dataScannedinGB=('dataScannedInGB', 'sum'), \
    scanTimeInHrs=('processingTimeinHrs', 'sum'), \
    IdleTimeInHrs=('IdleTimeInHrs', 'sum'), \
    numFilesScanned=('numberOfFilesScanned', 'sum'), \
    uniqPodCount=('uniqPodCount', 'max')).reset_index()
    df9['ts']=pd.to_datetime(df9['ts'],unit='ms')
    df9['avgFileSizeInMB']=df9['dataScannedinGB']*1000/df9['numFilesScanned']
    df9 = pd.melt(df9, id_vars=['appliance_id','ts', 'node_ip'], var_name='metrics', value_name='value').drop_duplicates()
    return df9

def loadPrometheusDataFromFileRegex(root, filePrefix, metricsArr, fileExtn, **kwargs):
    daterange = kwargs.get('daterange', None)
    df_arr = []
    for metricsName in metricsArr:
        for fileAggFunc in ['max', 'avg']:
            aggfunction = 'mean'
            if(fileAggFunc == 'max'):
                aggfunction = 'max'
            df_tmp = loadPrometheusData(root, filePrefix, metricsName, fileAggFunc, fileExtn, aggfunction, daterange=daterange)
            df_arr.append(df_tmp)

    df = pd.concat(df_arr, ignore_index=True)
    return df

def loadApplianceTimeSeriesData(root, metricsArr, daterange):
    dfsp = loadConnectorDataFromFileRegex(root, 'SCANPROC-*.csv', daterange=daterange)
    dfst = loadStrucDataFromFileRegex(root, 'STRUCTURED-*.csv', daterange=daterange)
    df = loadPrometheusDataFromFileRegex(root, 'securiti_appliance_', metricsArr, '.csv', daterange=daterange)
    dfus = loadUnstrucDataFromFileRegex(root, 'UNSTRUCTURED-*.csv', daterange=daterange)
    df = pd.concat([df, dfus, dfst, dfsp], ignore_index=True)
    df['value'] = df.value.astype(float)
    df = df[(df.value > 0)]
    return df