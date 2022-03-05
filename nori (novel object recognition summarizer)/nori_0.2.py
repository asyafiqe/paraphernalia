#!/usr/bin/env python
# coding: utf-8

# # nori
# Novel Object Recognition data Interpreter
# 
# (A simple script to summarize novel object recognition result)

# title
nori_title = '''                          
░█▀█░█▀█░█▀▄░▀█▀
░█░█░█░█░█▀▄░░█░
░▀░▀░▀▀▀░▀░▀░▀▀▀ '''                          
print('initializing nori v0.2...')
print(nori_title)
print('Novel Object Recognition data Interpreter \n')
print('by Abdullah Syafiq, 2022')
print('================================================ \n')

# check if pandas had been installed
print('checking dependencies...')

import sys
import subprocess
import pkg_resources

required = {'pandas','openpyxl'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing])
    
print('all dependencies are met')

# import necessary libraries
print('importing libraries...')
import pandas as pd
import openpyxl
import os

# use os.walk to get all the result.txt files 
# in the subdirectories
print('searching result.txt files...')
path = os.getcwd()

result_txt = []
for root, dirs, files in os.walk(path):
	for file in files:
		if(file.endswith("result.txt")):
			result_txt.append(os.path.join(root,file))

# print number of result.txt
no_files = len(result_txt)
print('================================================ \n')
print('processing {0} files... \n'.format(no_files))
print('================================================')

# make directory for output
print('creating output directory... \n')
os.makedirs("output", exist_ok=True)

# convert txt to xlsx
for f in result_txt:
    # extract filename
    filename = os.path.splitext(os.path.split(f)[1])[0]
    
    # import result.txt
    df = pd.read_csv(f, sep="\t", header=None, encoding="ISO-8859-1")
    
    # export to excel file
    df.to_excel('output/' + filename + '.xlsx', index = False, header=False)

print('{0} result files had been converted to xlsx... \n'.format(no_files))

# declare column name
col_names = ['box_no','animal_id','group','tot_dis','tot_mov_dur','tot_imo_dur','tot_mov_eps_no','avg_spd','mvg_spd','dist_per_mov','dur_per_mov','wall_side_time','ctr_reg_time','ctr_reg_pct','1_blk','2_blk','3_blk','4_blk','5_blk','6_blk','7_blk','8_blk','9_blk','10_blk','11_blk','12_blk','13_blk','14_blk','15_blk','16_blk','17_blk','18_blk','19_blk','20_blk','21_blk','22_blk','23_blk','24_blk','25_blk','26_blk','27_blk','28_blk','29_blk','30_blk','31_blk','32_blk','33_blk','34_blk','35_blk','36_blk','subroi1_times_entered','subroi1_stay_time','subroi2_times_entered','subroi2_stay_time']

# create dataframe from all result.txt
txt_df = pd.concat([pd.read_csv(f, sep="\t", usecols = range(0,54), \
                                names = col_names, skiprows = 43, \
                                encoding = 'unicode_escape') for f in result_txt ], \
                   ignore_index=True)

# create function for quadrant duration calculation
def calc_q1(row):
    return row['1_blk'] + row['2_blk'] + row['3_blk'] \
        + row['7_blk'] + row['8_blk'] + row['9_blk'] \
        + row['13_blk'] + row['14_blk'] + row['15_blk']
        
def calc_q2(row):
    return row['22_blk'] + row['23_blk'] + row['24_blk'] \
        + row['28_blk'] + row['29_blk'] + row['30_blk'] \
        + row['34_blk'] + row['35_blk'] + row['36_blk']
        
def calc_q3(row):
    return row['4_blk'] + row['5_blk'] + row['6_blk'] \
        + row['10_blk'] + row['11_blk'] + row['12_blk'] \
        + row['16_blk'] + row['17_blk'] + row['18_blk']
 
def calc_q4(row):
    return row['19_blk'] + row['20_blk'] + row['21_blk'] \
        + row['25_blk'] + row['26_blk'] + row['27_blk'] \
        + row['31_blk'] + row['32_blk'] + row['33_blk']

# calculate quadrant duration
print('calculating quadrant duration...')
txt_df['q1'] = txt_df.apply(calc_q1, axis=1)
txt_df['q2'] = txt_df.apply(calc_q2, axis=1)
txt_df['q3'] = txt_df.apply(calc_q3, axis=1)
txt_df['q4'] = txt_df.apply(calc_q4, axis=1)

# import sample_list.csv
print('importing sample list...')
if os.path.exists('sample_list.csv')==True:
    sample_list = pd.read_csv('sample_list.csv')
else:
    print('================================================ \n')
    print("sample_list.csv not found \n")
    print('================================================ \n')
    os.system('pause')

# left merge sample_list
txt_df = pd.merge(txt_df, sample_list, how="left", on=["animal_id"])

# create function for behavioral indices
def calc_exploration(row):
    return (row['q1'] + row['q2']) / (row['q1'] + row['q2'] + row['q3'] + row['q4'])

def calc_discrimination_roi(row):
    return (row['subroi1_stay_time'] - row['subroi2_stay_time']) / (row['subroi1_stay_time'] + row['subroi2_stay_time']) \
        if row['novel_object_location']==1 \
            else ((row['subroi2_stay_time'] - row['subroi1_stay_time']) / (row['subroi1_stay_time'] + row['subroi2_stay_time']) \
                  if row['novel_object_location']==2 \
                      else 'incorrect novel_object_location value')
                
def calc_preference_roi(row):
    return row['subroi1_stay_time'] / (row['subroi1_stay_time'] + row['subroi2_stay_time']) \
        if row['novel_object_location']==1 \
            else (row['subroi2_stay_time'] / (row['subroi1_stay_time'] + row['subroi2_stay_time']) \
                  if row['novel_object_location']==2 \
                      else 'incorrect novel_object_location value')

# calculate behavioral indices (conditional)
print('calculating behavioral indices...')
txt_df['object_exploration_value'] = txt_df.apply(calc_exploration, axis=1)
txt_df['discrimination_index'] = txt_df.apply(calc_discrimination_roi, axis=1)
txt_df['preference_index'] = txt_df.apply(calc_preference_roi, axis=1)

#export to csv
print('exporting summary file...')
txt_df.to_csv( "output/" + "NOR_output.csv", index=False, encoding='utf-8-sig')

print('\nyour summaries are in output folder.. \n')

# show "Press any key..."
os.system('pause')
