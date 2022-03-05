#!/usr/bin/env python
# coding: utf-8

# # tanAbridge
# Abridge your TanaMove data!

# title
tanAbridge_title =  '''                                                                
  __            ___   __       _    __        
 / /____ ____  / _ | / /  ____(_)__/ /__ ____ 
/ __/ _ `/ _ \/ __ |/ _ \/ __/ / _  / _ `/ -_)
\__/\_,_/_//_/_/ |_/_.__/_/ /_/\_,_/\_, /\__/ 
                                   /___/      
'''                    
print('initializing tanAbridge v0.3...')
print(tanAbridge_title)
print('Abridge your TanaMove data! \n')
print('by Abdullah Syafiq, 2022')
print('================================================ \n')
#%%
# check if pandas, numpy, and openpxl had been installed
print('checking dependencies... \n')

import sys
import subprocess
import pkg_resources

required = {'pandas','numpy','openpyxl'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing])
#%%   
# import necessary libraries
print('importing libraries...')
import pandas as pd
import os
import glob
import numpy as np
import openpyxl #for read and write xlsx file. Needed by to_excel.

#%%
# make directory for output csv
print('creating output directory... \n')
os.makedirs("output", exist_ok=True)

#%%
# use glob to get all the csv files 
# in the folder
path = os.getcwd()
csv_files = glob.glob(os.path.join(path, "*.csv"))
no_files = len(csv_files)
print('================================================ \n')
print('processing {0} files... \n'.format(no_files))
print('================================================ \n')

#%%
col_names = ['counter', 'time', 'button']

#%%

summary_df = pd.DataFrame() #create dataframe to collect loop output
for f in csv_files: #loop in all csv files
    filename = os.path.splitext(os.path.split(f)[1])[0] #get filename without extension
    df = pd.read_csv(f, names = col_names, header = None, encoding = "UTF-8") #extract csv
    time_gap = df['counter'][0] #get time gap
    minute_dur = 1/time_gap*60 #calculate frame per minute
    #total_time = df['time'][0]
    #video_location = df['button'][0]
    df = df.drop(index=0) #delete first row(contain time gap, total duration, and video location)
    button_unique = df['button'].dropna().unique() #remove NaN, count unique character in button column
    ranges = np.arange(0, len(df)-1, minute_dur).astype(int) #make array of per minute ranges
    ranges = np.append(ranges, len(df)-1) #append last cell number (to complete last range)
        
    loop_df = pd.DataFrame() #create df to collect per file loop output
    for i in button_unique:
        a = [] #create blank list to collect per file loop output
        for index, elem in enumerate(ranges[:-1]): #using enumerate to access next index's value. Skip last index.
            a.append(df.button.iloc[elem:ranges[index+1]].isin([i]).sum()*time_gap) #specify row range per minute, find if i in range (return True of False), count True value.
        a.append(sum(a)) #append result to dummy list
        a.insert(0, filename) #add filename to first row
        loop_df[i] = a    #add result list to dataframe
    loop_df_transpose = loop_df.transpose() #after all button occurences counted, transpose the dataframe
    summary_df = pd.concat([summary_df, loop_df.transpose()], axis=0, join='outer') #combine all result in one dataframe #change from append to concat due to deprecated warning (?) (FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.)
     #loop_df_transpose.to_csv('output/' + filename + '_sum.csv', encoding='utf-8', index=True)

summary_df.reset_index(inplace=True) #convert index value (unique button) to column

#%%
print('exporting to xlsx...')

button_unique_all = summary_df.iloc[:, 0].dropna().unique()  #count unique character in button column of all csv (may varied between files) 
with pd.ExcelWriter("output\summary.xlsx") as writer: #export to excel
    for i in button_unique_all: #loop through all unique character in all csv
        df_temp = summary_df.loc[(summary_df.iloc[:, 0]==i), :] #filter row based on unique character
        df_temp.to_excel(writer, sheet_name=i, index=False) #export to excel sheet

#%%    

print('\nyour summaries are in output folder.. \n')
#%%
# show "Press any key..."
os.system('pause')
#%%