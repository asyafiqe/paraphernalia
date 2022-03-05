#!/usr/bin/env python
# coding: utf-8

# # lumos
# LUdicrous light-dark box Measurement Summarizer
# 
# Licht Und dunkel kasten Messung Summe skript
# 
# (A simple script to summarize light-dark box result)

# title
lumos_title = ''' (                         
 )\   (      )             
((_) ))\    (      (   (   
 _  /((_)   )\  '  )\  )\  
| |(_))(  _((_))  ((_)((_) 
| || || || '  \()/ _ \(_-< 
|_| \_,_||_|_|_| \___//__/ '''                          
print('initializing lumos v0.1... \n')
print(lumos_title)
print('LUdicrous light-dark box Measurement Summarizer')
print('Licht Und dunkel kasten Messung Summe skript \n')
print('by Abdullah Syafiq, 2022')
print('================================================ \n')

# check if pandas had been installed
print('checking dependencies... \n')

import sys
import subprocess
import pkg_resources

required = {'pandas'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing])
    
print('all dependencies are met \n')

# import necessary libraries
import pandas as pd
import os
import glob

print('importing libraries... \n')

# assign columns name
col_names = ['dist_light', 'dist_dark', 'rise_light', 'rise_dark', 'transfer_num','time_light', 'time_dark', 'transfer_latency']

# make directory for output csv
print('creating output directory... \n')
os.makedirs("output", exist_ok=True)

# use glob to get all the csv files 
# in the folder
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))
no_files = len(csv_files)
print('================================================ \n')
print('processing {0} files... \n'.format(no_files))
print('================================================ \n')

for f in csv_files:
    # extract filename
    filename_ext = os.path.basename(f)
    filename = os.path.splitext(os.path.split(f)[1])[0]
    
    # assign columns name
    col_names = ['dist_light', 'dist_dark', 'rise_light', 'rise_dark', 'transfer_num',                  'time_light', 'time_dark', 'transfer_latency']
    
    # create data frame from csv
    df = pd.read_csv(f, usecols = range(3, 11), names = col_names, skiprows = 13, nrows = 10, header = None, encoding = 'unicode_escape')
    
    # calculate
    dist_ratio_1_5mins = df.dist_light.iloc[0:5].sum() / (df.dist_light.iloc[0:5].sum() + df.dist_dark.iloc[0:5].sum())
    dist_ratio_5_10mins = df.dist_light.iloc[5:10].sum() / (df.dist_light.iloc[5:10].sum() + df.dist_dark.iloc[5:10].sum())
    dist_ratio_10mins = df.dist_light.sum() / (df.dist_light.sum() + df.dist_dark.sum())

    rise_ratio_1_5mins = df.rise_light.iloc[0:5].sum() / (df.rise_light.iloc[0:5].sum() + df.rise_dark.iloc[0:5].sum())
    rise_ratio_5_10mins = df.rise_light.iloc[5:10].sum() / (df.rise_light.iloc[5:10].sum() + df.rise_dark.iloc[5:10].sum())
    rise_ratio_10mins = df.rise_light.sum() / (df.rise_light.sum() + df.rise_dark.sum())

    no_of_transfer_1_5mins = df.transfer_num.iloc[0:5].sum()
    no_of_transfer_5_10mins = df.transfer_num.iloc[5:10].sum()
    no_of_transfer_10mins = df.transfer_num.sum()

    time_ratio_1_5mins = df.time_light.iloc[0:5].sum() / (df.time_light.iloc[0:5].sum() + df.time_dark.iloc[0:5].sum())
    time_ratio_5_10mins = df.time_light.iloc[5:10].sum() / (df.time_light.iloc[5:10].sum() + df.time_dark.iloc[5:10].sum())
    time_ratio_10mins  = df.time_light.sum() / (df.time_light.sum() + df.time_dark.sum())

    transfer_latency_1_5mins = df.transfer_latency.iloc[0:5].sum()
    transfer_latency_5_10mins = df.transfer_latency.iloc[5:10].sum()
    transfer_latency_10mins = df.transfer_latency.sum()

    distance_1_5mins = df.dist_light.iloc[0:5].sum() + df.dist_dark.iloc[0:5].sum()
    distance_5_10mins = df.dist_light.iloc[5:10].sum() + df.dist_dark.iloc[5:10].sum()
    distance_10mins = df.dist_light.sum() + df.dist_dark.sum()

    distance_light_1_5mins = df.dist_light.iloc[0:5].sum()
    distance_light_5_10mins = df.dist_light.iloc[5:10].sum()
    distance_light_10mins = df.dist_light.sum()
    
    time_light_1_5mins = df.time_light.iloc[0:5].sum()
    time_light_5_10mins = df.time_light.iloc[5:10].sum()
    time_light_10mins = df.time_light.sum()
    
    # create summary list
    summary = {'distance ratio 1-5mins':dist_ratio_1_5mins,                'distance ratio 5-10mins':dist_ratio_5_10mins,                'distance ratio 10mins':dist_ratio_10mins,                
               'rise ratio 1-5mins':rise_ratio_1_5mins, \
               'rise ratio 5-10mins':rise_ratio_5_10mins, \
               'rise ratio 10mins':rise_ratio_10mins, \
           
               'no. of transfer 1-5mins':no_of_transfer_1_5mins, \
               'no. of transfer 5-10mins':no_of_transfer_5_10mins, \
               'no. of transfer 10mins':no_of_transfer_10mins, \
           
               'time ratio 1-5mins':time_ratio_1_5mins, \
               'time ratio 5-10mins':time_ratio_5_10mins, \
               'time ratio 10mins':time_ratio_10mins, \
           
               'transfer latency 1-5mins':transfer_latency_1_5mins, \
               'transfer latency 5-10mins':transfer_latency_5_10mins, \
               'transfer latency 10mins':transfer_latency_10mins, \
           
               'distance 1-5mins':distance_1_5mins, \
               'distance 5-10mins':distance_5_10mins, \
               'distance 10mins':distance_10mins, \
           
               'distance light 1-5mins':distance_light_1_5mins, \
               'distance light 5-10mins':distance_light_5_10mins, \
               'distance light 10mins':distance_light_10mins, \
           
               'time light 1-5mins':time_light_1_5mins, \
               'time light 5-10mins':time_light_5_10mins, \
               'time light 10mins':time_light_10mins}
    
    # create summary dataframe (index name = filename)
    summary_df = pd.DataFrame(summary, index = [filename])
    
    # export summary dataframe to csv
    summary_df.to_csv('output/' + filename_ext, encoding='utf-8', index=True)

# list all output csv files
output_csv_files = glob.glob(os.path.join(path, 'output', "*.csv"))

# concatenate all csv on output folder
combined_csv = pd.concat([pd.read_csv(f) for f in output_csv_files ])

# rename first column
combined_csv.columns = ['filename', *combined_csv.columns[1:]]

#export to csv
print('exporting combined summary file... \n')
combined_csv.to_csv( "output/" + "combined_output.csv", index=False, encoding='utf-8-sig')

print('\nyour summaries are in output folder.. \n')

# show "Press any key..."
os.system('pause')


