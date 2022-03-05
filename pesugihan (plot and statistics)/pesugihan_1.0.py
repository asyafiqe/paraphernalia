#!/usr/bin/env python
# coding: utf-8
# pesugihan
# Pengouin and Seaborn powered Utility for Graphic generation with statistical ANalysis
# 
# (A simple script to generate statistics and graph powered by Pengouin and Seaborn)

# title
#%%
# title
pesugihan_title = '''                          
.______    _______     _______. __    __    _______  __   __    __       ___      .__   __. 
|   _  \  |   ____|   /       ||  |  |  |  /  _____||  | |  |  |  |     /   \     |  \ |  | 
|  |_)  | |  |__     |   (----`|  |  |  | |  |  __  |  | |  |__|  |    /  ^  \    |   \|  | 
|   ___/  |   __|     \   \    |  |  |  | |  | |_ | |  | |   __   |   /  /_\  \   |  . `  | 
|  |      |  |____.----)   |   |  `--'  | |  |__| | |  | |  |  |  |  /  _____  \  |  |\   | 
| _|      |_______|_______/     \______/   \______| |__| |__|  |__| /__/     \__\ |__| \__| 
'''                          
print('initializing pesugihan v1.0...')
print(pesugihan_title)
print('Pengouin and Seaborn powered Utility for Graphic generation with statistical ANalysis \n')
print('by Abdullah Syafiq, 2022')
print('================================================ \n')
#%%
# check if dependencies had been installed
print('checking dependencies...')

import sys
import subprocess
import pkg_resources

required = {'pandas','pingouin', 'seaborn', 'statannotations', 'matplotlib','numpy', 'openpyxl'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing])
    
print('all dependencies are met')

# import necessary libraries
print('importing libraries...')
print('importing pandas')
import pandas as pd
print('importing pingouin')
import pingouin as pg
print('importing seaborn')
import seaborn as sns
print('importing Annotator')
from statannotations.Annotator import Annotator
print('importing pyplot')
import matplotlib.pyplot as plt
print('importing numpy')
import numpy as np
print('importing openpyxl')
import openpyxl #for exporting to excel
import itertools #needed for 'zip' in iterable loops, and also itertools.combination
import glob
import os


#%%
def check_file(x):
    return len(glob.glob(x))

#%%
def normality_test(x_df):
    #https://stackoverflow.com/questions/30635145/create-multiple-dataframes-in-loop
    #create dictionary to put dataframe
    d = {} 
    
    #create dataframe name based on df.columns
    for x in variable_names: 
        d[x] = pd.DataFrame()

    #run normality test
    for x in variable_names:
        d[x] = d[x].append(pg.normality(data = x_df, dv = x, group = group_column, method = 'shapiro'))
        d[x].reset_index(inplace=True) #convert index to first column
        d[x] = d[x].rename(columns={ 'index':'group'}) #rename first column

    #merge normality test result

    #add subject name to first column of normality test dataframe
    for x in variable_names:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to normality test dataframe

    normality_t_df = pd.concat(d.values(), ignore_index=True) #merge all dataframe in dictionary
    normality_nnd_t_df = normality_t_df.loc[(normality_t_df.normal == False)].reset_index(drop=True) #show not equal variance variable
    
    return normality_t_df, normality_nnd_t_df
#%%
def homoscedasticity_test(x_df):
    #create dictionary to put dataframe
    d = {} 
    #create dataframe name based on df.columns
    for x in variable_names: 
        d[x] = pd.DataFrame()
        
    #run homoscedasticity test
    for x in variable_names:
        d[x] = d[x].append(pg.homoscedasticity(data=x_df, dv=x, group=group_column, method='levene'))
        d[x].reset_index(inplace=True) #convert index to first column
        d[x] = d[x].rename(columns={ 'index':'group'}) #rename first column
        
    #merge homoscedasticity test result

    #add subject name to first column of homoscedasticity test dataframe
    for x in variable_names:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to homoscedasticity test dataframe

    homoscedasticity_t_df = pd.concat(d.values(), ignore_index=True) #merge all dataframe in dictionary
    homoscedasticity_notequal_t_df = homoscedasticity_t_df.loc[(homoscedasticity_t_df.equal_var == False)].reset_index(drop=True) #show not equal variance variable
    
    return homoscedasticity_t_df, homoscedasticity_notequal_t_df      
#%%
# ANOVA (normal distribution, equal variance)  
def anova_test(x_df):
    #create dictionary to put dataframe
    d = {} 

    #create dataframe name based on df.columns
    for x in omni_anova: 
        d[x] = pd.DataFrame()

    #run ANOVA
    for x in omni_anova:
        d[x] = d[x].append(pg.anova(data=x_df, dv=x, between=group_column, detailed=True))

    #combining ANOVA result into one big dataframe

    #add subject name to first column of ANOVA test dataframe
    for x in omni_anova:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to ANOVA test dataframe

    #merge all dataframe in dictionary
    anova_t_df = pd.concat(d.values(), ignore_index=True)

    #show only significant
    anova_t_sig_df = anova_t_df.loc[anova_t_df['p-unc'] <= 0.05].reset_index(drop=True)
    
    return anova_t_df, anova_t_sig_df
#%%
#post-hoc Tukey
def tukey_test(x_df):
   #create dictionary to put dataframe
   d = {}

   #create dataframe name based on df.columns
   for x in anova_sig_df.variable: 
       d[x] = pd.DataFrame()

   #run Tukey
   for x in d:
       d[x] = d[x].append(pg.pairwise_tukey(data=x_df, dv=x, between=group_column, effsize='hedges'))

   #combining Tukey result into one big dataframe

   #add subject name to first column of ANOVA test dataframe
   for x in d:
       D = {'variable': x} #create list for new dataframe
       new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
       d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to ANOVA test dataframe

   #merge all dataframe in dictionary
   tukey_t_df = pd.concat(d.values(), ignore_index=True)

   #show only significant
   tukey_t_sig_df = tukey_t_df.loc[tukey_t_df['p-tukey'] <= 0.05].reset_index(drop=True)
   
   return tukey_t_df, tukey_t_sig_df
#%%
# Welch ANOVA (normal distribution, non-equal variance)
def welch_test(x_df):
    

    #create dictionary to put dataframe
    d = {} 

    #create dataframe name based on df.columns
    for x in omni_welch: 
        d[x] = pd.DataFrame()

    #run Welch ANOVA
    for x in d:
        d[x] = d[x].append(pg.welch_anova(data=x_df, dv=x, between=group_column))

    #combining Welch ANOVA result into one big dataframe

    #add subject name to first column of welch ANOVA test dataframe
    for x in d:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to welch ANOVA test dataframe

    #merge all dataframe in dictionary
    welch_t_df = pd.concat(d.values(), ignore_index=True)

    #show only significant
    welch_t_sig_df = welch_t_df.loc[welch_t_df['p-unc'] <= 0.05].reset_index(drop=True) 
    
    return welch_t_df, welch_t_sig_df
#%%
#post-hoc Games-Howell (for welch)
#https://www.reddit.com/r/statistics/comments/ay7zsf/welchs_anova_post_hoc_in_r/
#https://pingouin-stats.org/guidelines.html
def games_test(x_df):
    #create dictionary to put dataframe
    d = {}
    
    #create dataframe name based on df.columns
    for x in welch_sig_df.variable: 
        d[x] = pd.DataFrame()
    
    #run Games-Howell
    for x in d:
        d[x] = d[x].append(pg.pairwise_gameshowell(data=x_df, dv=x, between=group_column, effsize='hedges'))

    #combining post-hoc Games-Howell (for welch) result into one big dataframe

    #add subject name to first column of post-hoc Games-Howell (for welch) test dataframe
    for x in d:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to ANOVA test dataframe

    #merge all dataframe in dictionary
    games_t_df = pd.concat(d.values(), ignore_index=True)

    #show only significant
    games_t_sig_df = games_t_df.loc[games_t_df['pval'] <= 0.05].reset_index(drop=True)
    
    return games_t_df, games_t_sig_df
#%%
# Test for not normally distributed data
# Kruskal-Wallis H

def nonparam_test(x_df):
    #create dictionary to put dataframe
    d = {} 
    #create dataframe name based on df.columns
    for x in omni_nonparam: 
        d[x] = pd.DataFrame()
    
    #run Kruskal-Wallis H
    for x in d:
        d[x] = d[x].append(pg.kruskal(data=x_df, dv=x, between=group_column))
        d[x].reset_index(inplace=True) #convert index to first column
        d[x] = d[x].rename(columns={ 'index':'group'}) #rename first column

    #combining Kruskal-Wallis H result into one big dataframe

    #add subject name to first column of Kruskal-Wallis H test dataframe
    for x in d:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to ANOVA test dataframe

    #merge all dataframe in dictionary
    kruskal_t_df = pd.concat(d.values(), ignore_index=True)

    #show only significant
    kruskal_t_sig_df = kruskal_t_df.loc[kruskal_t_df['p-unc'] <= 0.05].reset_index(drop=True) 

    return kruskal_t_df, kruskal_t_sig_df
#%%
#post-hoc Sidak(nonparametric)

def sidak_test(x_df):
    #create dictionary to put dataframe
    d = {} 
    #create dataframe name based on df.columns
    for x in kruskal_sig_df.variable: 
        d[x] = pd.DataFrame()
        
    for x in d:
        d[x] = d[x].append(pg.pairwise_ttests(data=x_df, dv=x, between=group_column, parametric=False, padjust = 'sidak', effsize='hedges'))
        #d[x].reset_index(inplace=True) #convert index to first column
        #d[x] = d[x].rename(columns={ 'index':'subject'}) #rename first column

    #combining Hoc Sidak(nonparametric) result into one big dataframe
    
    #add subject name to first column of Hoc Sidak(nonparametric) test dataframe
    for x in d:
        D = {'variable': x} #create list for new dataframe
        new_col_df = pd.DataFrame(D, index=d[x].index) #create new dataframe to be merged. Create number of row equal to number of row in target dataframe
        d[x] = pd.concat([new_col_df, d[x]], axis = 1) #merge subject name column to ANOVA test dataframe

    #merge all dataframe in dictionary
    sidak_t_df = pd.concat(d.values(), ignore_index=True)
    
    #show only significant
    sidak_t_sig_df = sidak_t_df.loc[sidak_t_df['p-corr'] <= 0.05].reset_index(drop=True) 
    
    return sidak_t_df, sidak_t_sig_df
#%%
def graph_only():
    print('generating graph...')
    #create pair combination df
    pairs_df = pd.DataFrame(itertools.combinations(group_unique, 2))
    #convert to list (df is not iterable)
    pairs = pairs_df.values.tolist()
    for (x, a, b) in zip(range(len(variable_names)), #detect the index
                         variable_names, 
                         unit_df.iloc[0] ##select first row
                         ):
        plotting_parameters = {
        'data':    df,
        'x':       df.columns[0],
        'y':       a}
        
        # grid backround style
        sns.set_style('darkgrid')    
        
        #declare boxplot    
        ax = sns.boxplot(**plotting_parameters,
                         palette="Set2")#'viridis''Set2''colorblind'

        # add jitter
        sns.swarmplot(**plotting_parameters,
                           #jitter color
                           color='white', edgecolor='black', 
                           #jitter size
                           linewidth=1.5, size=5)

        # add annotation
        annotator = Annotator(ax, pairs, **plotting_parameters)
        annotator.configure(test="Mann-Whitney", comparisons_correction="bonferroni", text_format="star") #text_format: simple, full, star
        _, corrected_results = annotator.apply_and_annotate()


        #label
        plt.title(a)
        plt.xlabel(df.columns[0])
        plt.ylabel(b)
        #export to png
        #sns_plot.figure.savefig("output.png")
        #plt.savefig('save_as_a_png.png')
        plt.savefig('output/' + a + '.png', dpi=300, 
                    #transparent=True
                    )
        plt.savefig('saving-a-seaborn-plot-as-eps-file-300dpi.eps',
               dpi=300)
        #plt.show()
        plt.clf() # this clears the figure
        #print(x,a,b)
        print('generating '+ str(x+1) +' graph(s) out of ' + str(len(variable_names)))

#%%
#Graph with significant omnibus
def graph_sig_omni():
    print('generating graph...')

    for (x, a, b) in zip(range(len(var_sig_omni)), #detect the index
                         var_sig_omni, 
                         unit_df.iloc[0] ##select first row
                         ):
        plotting_parameters = {
        'data':    df,
        'x':       df.columns[0],
        'y':       a} #'viridis'
        
        # grid backround style
        sns.set_style('darkgrid')  
        
        #declare boxplot  
        ax = sns.boxplot(**plotting_parameters)

        # add jitter
        sns.swarmplot(**plotting_parameters, 
                           #jitter color
                           color='white', edgecolor='black', 
                           #jitter size
                           linewidth=1.5, size=5)
        # Add annotations
        annotator = Annotator(ax, pairs, **plotting_parameters)
        annotator.set_pvalues_and_annotate(pairwise_df[a])
        
        #label
        plt.title(a)
        plt.xlabel(df.columns[0])
        plt.ylabel(b)
        #export to png
        #sns_plot.figure.savefig("output.png")
        #plt.savefig('save_as_a_png.png')
        plt.savefig('output/' + a + '.png', dpi=300, 
                    #transparent=True
                    )
        #plt.show()
        plt.clf() # this clears the figure
        #print(x,a,b)
        print('generating '+ str(x+1) +' graph(s) out of ' + str(len(var_sig_omni)))

#%%

#Graph with non significant omnibus
def graph_notsig_omni():
    print('generating graph...')
    for (x, a, b) in zip(range(len(var_notsig_omni)), #detect the index
                         var_notsig_omni, 
                         unit_df.iloc[0] ##select first row
                         ):
        plotting_parameters = {
        'data':    df,
        'x':       df.columns[0],
        'y':       a
        } #'viridis'
        
        # grid backround style
        sns.set_style('darkgrid')
        
        ax = sns.boxplot(**plotting_parameters, 
                         palette= 'Set2')

        # add jitter
        sns.swarmplot(**plotting_parameters, 
                           #jitter color
                           color='white', edgecolor='black', 
                           #jitter size
                           linewidth=1.5, size=5)

        
        
        #label
        plt.title(a)
        plt.xlabel('subject')
        plt.ylabel(b)
        #export to png
        #sns_plot.figure.savefig("output.png")
        #plt.savefig('save_as_a_png.png')
        plt.savefig('output/' + a + '.png', dpi=300, 
                    #transparent=True
                    )
        plt.show()
        plt.clf() # this clears the figure
        #print(x,a,b)
        print('generating '+ str(x+1) +' graph(s) out of ' + str(len(var_notsig_omni)))
#%%
#%%

#%%
if check_file('*tumbal.csv') > 0:
    csv_files = glob.glob('*tumbal.csv')
    df_filename = os.path.splitext(csv_files[0])[0]
elif check_file('*tumbal.xlsx') > 0:
    xlsx_files = glob.glob('*tumbal.xlsx')
    df_filename = os.path.splitext(xlsx_files[0])[0]
else:
    print('no file ends with tumbal.csv or tumbal.xlsx was found')
    os.system('pause')
    sys.exit()

print('importing file....')
if "csv_files" in globals():
    df = pd.read_csv(csv_files[0], header = 0, encoding = "UTF-8")
elif "xlsx_files" in globals():
    df = pd.read_excel(xlsx_files[0], header = 0)
else: 
    print('failed to import file')
    os.system('pause')
    sys.exit()

df.columns = df.columns.str.replace('_',' ')
#clear out all blank column
df.dropna(how='all', axis=1, inplace=True)
#%%
#import unit csv
print('importing unit csv...')
column_unit = 'column_unit' 
if check_file(f'{column_unit}.csv') > 0:
    unit_df = pd.read_csv(f'{column_unit}.csv', header = 0, encoding = "UTF-8").iloc[:, 2:]
elif check_file(f'{column_unit}.xlsx') > 0:
    unit_df = pd.read_excel(f'{column_unit}.xlsx', header = 0).iloc[:, 2:]
else:
    print('column_unit.csv not found')

# make directory for output
print('creating output directory... \n')
os.makedirs("output", exist_ok=True)

#%%
# check number of sample
print('checking sample size...')
group_unique = np.unique(df.iloc[:,0])
variable_names = list(df.columns[2:])
group_column = df.columns[0]

sample_size = []
for i in group_unique:
    sample_size.append((df.iloc[:,0].values == i).sum())

if min(sample_size) < 4:
    print('\nsome group(s) had less than 3 samples')
    print('statistics table will not be generated')
    print('only graph will be generated')
    print('pairwise comparison with Mann-Whitney U and Bonferoni correction')
    os.system('pause')
    graph_only()
    os.system('pause')
    sys.exit()
    
#%%    
normality_df, normality_nnd_df = normality_test(df)
homoscedasticity_df, homoscedasticity_notequal_df = homoscedasticity_test(df)

#%%
#combine normality and variance result

#summary of normality result
norm_var_sum_df = pd.DataFrame()
for x in variable_names: #check per variable
    # filter normality result by group, check if all subject normally distributed, 
    # return False if one of them not normally distributed
    a = [all(normality_df[normality_df['variable'] == x].normal)]
    # append new column to df
    norm_var_sum_df[x] = a

norm_var_sum_df = norm_var_sum_df.transpose()
norm_var_sum_df.reset_index(inplace=True)
norm_var_sum_df = norm_var_sum_df.rename(columns = {'index': 'variable', 0: 'normal_dist'})

#concatenate with variance result
norm_var_sum_df = norm_var_sum_df.merge(homoscedasticity_df[['variable', 'equal_var']], how="left")

#%%
#make list of variable based on normality and variance result

def omnibus_classifier (row): #create classifier function to be applied later with lambda
    if row['normal_dist'] and row['equal_var']:
        return 'anova'
    elif row['normal_dist'] and (row['equal_var']==False):
        return 'welch'
    else:
        return 'nonparam'

#create new column based on the classification
norm_var_sum_df['omnibus'] = norm_var_sum_df.apply (lambda row: omnibus_classifier(row), axis=1)

#split dataframe based on omnibus test
omni_anova = list(norm_var_sum_df[norm_var_sum_df['omnibus'] == 'anova']['variable'])
omni_welch = list(norm_var_sum_df[norm_var_sum_df['omnibus'] == 'welch']['variable'])
omni_nonparam = list(norm_var_sum_df[norm_var_sum_df['omnibus'] == 'nonparam']['variable'])
#%%
# run omnibus and post-hoc test
if 'anova' in norm_var_sum_df.iloc[:,-1].values:
    anova_df, anova_sig_df = anova_test(df)
    if not anova_sig_df.empty:
        tukey_df, tukey_sig_df = tukey_test(df)
    
if 'welch' in norm_var_sum_df.iloc[:,-1].values:
    welch_df, welch_sig_df = welch_test(df)
    if not welch_sig_df.empty:
        games_df, games_sig_df = games_test(df)
    
if 'nonparam' in norm_var_sum_df.iloc[:,-1].values:
    kruskal_df, kruskal_sig_df = nonparam_test(df)
    if not kruskal_sig_df.empty:
        sidak_df, sidak_sig_df =  sidak_test(df)
#%%
# make list of significant omnibus
var_sig_omni_df = pd.DataFrame() #create empty dataframe
if 'anova_sig_df' in vars():
    var_sig_omni_df = pd.concat([var_sig_omni_df, anova_sig_df.variable]) #concat anova significant variable
if 'welch_sig_df' in vars():
    var_sig_omni_df = pd.concat([var_sig_omni_df, welch_sig_df.variable])  #concat welch significant variable
if 'kruskal_sig_df' in vars():
    var_sig_omni_df = pd.concat([var_sig_omni_df, kruskal_sig_df.variable])  #concat kruskal significant variable

var_sig_omni = var_sig_omni_df.values.tolist() #convert df to list(list of list)

var_sig_omni = [str(item[0]) for item in var_sig_omni] #list comprehension to convert list of list to simple list

var_notsig_omni = list(set(variable_names) - set(var_sig_omni)) #substract all variables with omnibus significant variables (list can't directly substracted, hence set and convert to list again)

#%%
# make dataframe with pair name

# extract pairs from post-hoc result 
# (more reliable than creating pairs directly with itertools combinations)
# pd.DataFrame(combinations(group_unique, 2))

if 'tukey_df' in vars():
    if not tukey_df.empty:
        pairwise_df=tukey_df[tukey_df['variable'] == tukey_df.variable[0]][['A', 'B']]

elif 'games_df' in vars():
    if not games_df.empty:
        pairwise_df=games_df[games_df['variable'] == games_df[0]][['A', 'B']]
elif 'sidak_df' in vars():  
    if not sidak_df.empty:
        pairwise_df=sidak_df[sidak_df['variable'] == omni_nonparam[0]][['A', 'B']]
else:
    print('no pair on all post-hoc')

#extract pair name
if 'pairwise_df' in vars():
    pairs = pairwise_df.values.tolist()

#adding ANOVA post-hoc (Tukey) to pairwise dataframe
if 'tukey_df' in vars():
    for x in anova_sig_df.variable:
        a = tukey_df[tukey_df['variable'] == x][['A','B','p-tukey']]
        a = a.rename(columns={'p-tukey':x})
        pairwise_df = pairwise_df.merge(a, how='left')

#adding Welch ANOVA post-hoc (Games-Howell) to pairwise dataframe
if 'games_df' in vars():
    for x in welch_sig_df.variable:
        a = games_df[games_df['variable'] == x][['A','B','pval']]
        a = a.rename(columns={'pval':x})
        pairwise_df = pairwise_df.merge(a, how='left')
    
#adding nonparametrik(KW) post-hoc (Sidak) to pairwise dataframe
if 'sidak_df' in vars():  
    for x in kruskal_sig_df.variable:
        a = sidak_df[sidak_df['variable'] == x][['A','B','p-corr']]
        a = a.rename(columns={'p-corr':x})
        pairwise_df = pairwise_df.merge(a, how='left')
#%%
#export result to excel
print('exporting list')
os.system('pause')

#create a excel writer object
with pd.ExcelWriter("output/" + df_filename + "_statistics.xlsx") as writer:
   
    #use to_excel function and specify the sheet_name and index
    #to store the dataframe in specified sheet
    normality_df.to_excel(writer, sheet_name="normality", index=False)
    normality_nnd_df.to_excel(writer, sheet_name="normality_nnd", index=False)
    homoscedasticity_df.to_excel(writer, sheet_name="homoscesdasticity", index=False)
    homoscedasticity_notequal_df.to_excel(writer, sheet_name="homoscesdasticity_notequal", index=False)
    norm_var_sum_df.to_excel(writer, sheet_name='dist_var', index=False)
    if 'anova_df' in vars():
        anova_df.to_excel(writer, sheet_name="anova", index=False)
    if 'anova_sig_df' in vars():
        anova_sig_df.to_excel(writer, sheet_name="anova_sig", index=False)
    if 'tukey_df' in vars():
        tukey_df.to_excel(writer, sheet_name="tukey", index=False)
    if 'tukey_sig_df' in vars():
        tukey_sig_df.to_excel(writer, sheet_name="tukey_sig", index=False)
    if 'welch_df' in vars():
        welch_df.to_excel(writer, sheet_name="welch", index=False)
    if 'welch_sig_df' in vars():
        welch_sig_df.to_excel(writer, sheet_name="welch_sig", index=False)
    if 'games_df' in vars():
        games_df.to_excel(writer, sheet_name="games", index=False)
    if 'games_sig_df' in vars():
        games_sig_df.to_excel(writer, sheet_name="games_sig", index=False)
    if 'kruskal_df' in vars():
        kruskal_df.to_excel(writer, sheet_name="kruskal", index=False)
    if 'kruskal_sig_df' in vars():
        kruskal_sig_df.to_excel(writer, sheet_name="kruskal_sig", index=False)
    if 'sidak_df' in vars():
        sidak_df.to_excel(writer, sheet_name="sidak", index=False)
    if 'sidak_sig_df' in vars():
        sidak_sig_df.to_excel(writer, sheet_name="sidak_sig", index=False)
    
#%%
## PLOTTING GRAPH
#%%
# change underscore in column name to space
df.columns = df.columns.str.replace('_',' ')
#df.columns = df.columns.str.replace(' ','_')

if 'var_sig_omni' in vars():
    if var_sig_omni:
        graph_sig_omni()
if 'var_notsig_omni' in vars():
    if var_notsig_omni:
        graph_notsig_omni()

#%%
print('\nyour graphs are in output folder.. \n')

# show "Press any key..."
os.system('pause')
#%%
# QQ plot
#subject_name = 'a01_3'
#variable_name = 'total_length'
#ax = pg.qqplot(df.loc[(df.subject == subject_name), variable_name], dist='norm')








