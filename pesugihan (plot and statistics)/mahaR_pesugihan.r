# MahaR Pesugihan (pesugihan on R)
# Mix stat Analysis and cHARt translated from PESUGIHAN
# 
# (A simple script to generate statistics and graph on R) 
#=============================
logo <- r"{

___  ___      _                 ______                     _ _                 
|  \/  |     | |                | ___ \                   (_) |                
| .  . | __ _| |__   __ _ _ __  | |_/ /__  ___ _   _  __ _ _| |__   __ _ _ __  
| |\/| |/ _` | '_ \ / _` | '__| |  __/ _ \/ __| | | |/ _` | | '_ \ / _` | '_ \ 
| |  | | (_| | | | | (_| | |    | | |  __/\__ \ |_| | (_| | | | | | (_| | | | |
\_|  |_/\__,_|_| |_|\__,_|_|    \_|  \___||___/\__,_|\__, |_|_| |_|\__,_|_| |_|
                                                      __/ |                    
                                                      |___/                     

}"
cat(logo)
cat("Mix stat Analysis and cHARt translated from PESUGIHAN")
cat("(A simple script to generate statistics and graph on R)") 
#=============================
# check dependencies
cat("checking dependencies")

## If a package is installed, it will be loaded. If any 
## are not, the missing package(s) will be installed 
## from CRAN and then loaded.

## List required packages
packages = c("caret", "tidyverse", "viridis", "rstatix","openxlsx","ggpubr")

## Load or install&load all
package.check <- lapply(
  packages,
  FUN = function(x) {
    if (!require(x, character.only = TRUE)) {
      install.packages(x, dependencies = TRUE)
      library(x, character.only = TRUE)
    }
  }
)

## load additional library from tidyverse
library(glue)
library(readxl)
cat("all dependencies are met")
#=============================
# check if tumbal exist
if (length(list.files(pattern = "tumbal\\.csv$")) > 0) {
  csv_files <- list.files(pattern = "tumbal\\.csv$")
  df_filename <- tools::file_path_sans_ext(csv_files[1])
} else if (length(list.files(pattern = "tumbal\\.xlsx$")) > 0) {
  xlsx_files <- list.files(pattern = "tumbal\\.xlsx$")
  df_filename <- tools::file_path_sans_ext(xlsx_files[1])
} else {
  cat('no file ends with tumbal.csv or tumbal.xlsx was found')
  stop('no file ends with tumbal.csv or tumbal.xlsx was found')
  exit()
}
#=============================
# import file to df
cat('importing file....')
if (exists("csv_files")) {
  ## import as df(compared to tibble(tidyverse read_csv) 
  ## read_csv is problematic for str2lang syntactically valid names
  df <- read.csv(file = csv_files[1]) 
} else if (exists("xlsx_files")) {
  df <- read_excel(file = xlsx_files[1])
} else {
  cat('failed to import file')
  stop('failed to import file')
  exit()
}
#=============================
#clear out all blank column
#https://stackoverflow.com/questions/2643939/remove-columns-from-dataframe-where-all-values-are-na
df <- Filter(function(x)!all(is.na(x)), df)
#=============================
## make list of unique groups
group_unique <- unique(df[,1])
## make list of numeric column
var_names <- colnames(select_if(df, is.numeric))
## rename first column
names(df)[1] <- "groups"

#!!!!!!!!!!!!!!!!!!df.columns = df.columns.str.replace('_',' ')!!!!!!!!!!!!!!!!!!
#=============================
#import unit csv
cat('importing unit csv...')
column_unit <- "column_unit" 

if (file.exists(glue('{column_unit}.csv'))) {
  unit_df <- read.csv(file = (glue('{column_unit}.csv'))) %>% select(var_names)
} else if (file.exists(glue('{column_unit}.xlsx'))) {
  unit_df <- read_excel(file = (glue('{column_unit}.xlsx'))) %>% select(var_names)
} else cat('column_unit.csv not found')

# make directory for output
cat('creating output directory... \n')
dir.create('output', showWarnings = FALSE)
dir.create('output/png', showWarnings = FALSE)
dir.create('output/pdf', showWarnings = FALSE)

#=============================
# check number of sample
cat('checking sample size...')
## count occurence on first column
sample_size <- table(df['groups'])

if (min(sample_size) < 4) {
  print('\nsome group(s) had less than 3 samples')
  print('statistics table will not be generated')
  print('only graph will be generated')
  print('pairwise comparison using t-test with Bonferoni correction')
  stop('not enough sample')
  pllot_graph_only()
  stop()
  exit()
}

#=============================
# identify group with near zero variance

## select only column with numeric var, group by groups, identify near zero variance group,
## save as tibble, add variable names as new column
nzvar <- df[,var_names] %>% group_by(df$groups) %>% 
group_modify(~ tibble(nearZeroVar(.x, saveMetrics = TRUE))) %>%
mutate(var = var_names)

## filter only variable with near zero variance
nzv_true <- nzvar %>% filter(nzv) %>% ungroup() %>% select(var)

## filter only unique variable
nzv_true_unique <- unique(nzv_true$var)

## create list of variable for normality test(all var - nzv)
var_for_norm_test <- var_names[!var_names %in% nzv_true_unique] 
#(alternative)setdiff(var_names, nzv_true_unique)

#=============================
# normality test with shapiro-wilk

## create blank df for downstream failsafe
normality_df <- data.frame()

normality_df <- df %>% 
  group_by(groups) %>% 
  shapiro_test(vars=var_for_norm_test)

## filter only not normally distributed var
normality_sig_df <- normality_df %>% filter(p <= 0.05)

#=============================
# homoscedasticity (bartlett)
homoscedasticity_df <- data.frame()

for(i in var_names){
  ## do bartlett test by groups, tidy to one liner, put into list
  a <- broom::tidy(bartlett.test(get(i) ~ groups, df))
  ## add variable name in first column
  a <- data.frame(variable = c(i), a)
  ## add temporary df to result df
  homoscedasticity_df <- rbind(homoscedasticity_df, a)
}
## add interpretation column
homoscedasticity_df <- homoscedasticity_df %>% mutate(equal_var = (p.value > 0.05))
## filter only unequal var
homoscedasticity_uev_df <- homoscedasticity_df %>% filter(equal_var = FALSE)

#=============================
# combine normality and homoscedasticity result

dist_var <- data.frame()

## loop for every variable
for (i in var_names){
  ## check if variable is not normally distributed or nzv(not included in normality test)
  if ((i %in% normality_sig_df[['variable']]) | (i %in% nzv_true_unique)) {
    ## assign as not normally distributed
    a <- data.frame(variable = i, normal_dist = c(FALSE))
    ## append to result df
    dist_var <- rbind(dist_var, a)
    
  } else {
    # anything else should be normal
    a <- data.frame(variable = c(i), normal_dist = c(TRUE))
    dist_var <- rbind(dist_var, a)
  }
}
# add variance data from homoscedasticity test
dist_var <- merge(x = dist_var, y = homoscedasticity_df %>% select(variable, equal_var), all.x = TRUE)

#=============================
# create list of omni test and its variables

## define function to classify omni test
omnibus_classifier <- function(row){
  x=as.logical(row['normal_dist'])
  y=as.logical(row['equal_var'])
  if (x & y){
    result <- 'anova'
  } else if (x & (y == FALSE)) {
    result <- 'welch'
  } else {
    result <- 'nonparam'
  }
  return(result)
}

## classify variables
dist_var <- dist_var %>% mutate(omnibus = apply(dist_var, 1, omnibus_classifier))

## create list per omni test
omni_anova <- purrr::flatten_chr(dist_var[dist_var$omnibus == 'anova',]['variable'])
omni_welch <- purrr::flatten_chr(dist_var[dist_var$omnibus == 'welch',]['variable'])
omni_nonparam <- purrr::flatten_chr(dist_var[dist_var$omnibus == 'nonparam',]['variable'])

#=============================
# ANOVA + tukey (function)(rstatix)
#https://stackoverflow.com/questions/61106658/one-way-anova-for-loop-how-do-i-iterate-through-multiple-columns-of-a-dataframe

anova_tukey_test <- function(var_list, daf){
  anova_df <- data.frame()
  anova_sig_df <- data.frame()
  tukey_df <- data.frame()
  anova_sig_df <- data.frame()
  
  for(i in var_list)
  {
    ## run ANOVA
    model <- (get(i) ~ groups)
    a <- anova_test(df, model)
    ## add variable name in first column
    a <- data.frame(variable = c(i), a)
    ## append to result df
    anova_df <- rbind(anova_df, a)
    
    ## if p sig, do Tukey
    if(a$p[1] <= 0.05) {
      b <- (tukey_hsd(df, model))
      ## add variable name column
      b <- data.frame(variable = i, b)
      ## append to result df
      tukey_df <- rbind(tukey_df, b)
    }
    
  }
  anova_df$method <- 'anova'
  anova_sig_df <- anova_df %>% filter(p<= 0.05) #show sig only
  tukey_sig_df <- tukey_df %>% filter(p.adj <= 0.05) #show sig only
  
  out <- list(anova_df, anova_sig_df, tukey_df, tukey_sig_df)
  return(out)
} 
#=============================
# Welch ANOVA + Games-Howell (function)
welch_anova_games_test <- function(var_list, daf) {
  welch_df <- data.frame()
  welch_sig_df <- data.frame()
  games_df <- data.frame()
  games_sig_df <- data.frame()
  
  for(i in var_list){
    ## do test, make it one-liner, put into temp df
    a <- tidyr::tibble(welch_anova_test(daf, get(i) ~ groups))
    ## add variable name to first column 
    a <- data.frame(variable = c(i), a)
    ## append temp df to result df
    welch_df <- rbind(welch_df, a)
  }
  welch_sig_df <- welch_df %>% filter(p <= 0.05)
  
  ## games if welch sig
  if (dim(welch_sig_df)[1] != 0){
    ## declare formula for games(rstatix)
    formulae <- lapply(welch_sig_df[,1], function(x) as.formula(glue("{x} ~ groups")))
    ## apply games howell on welch sig column
    b <- lapply(formulae, function(x) tibble(games_howell_test(x, data = daf)))
    ## convert list to df
    games_df <- data.table::rbindlist(b)
    ## rename first column
    names(games_df)[1] <- "variable"
    ## filter significant games
    games_sig_df <- games_df %>% filter(p.adj.signif != 'ns') 
  } 
  out <- list(welch_df, welch_sig_df, games_df, games_sig_df)
  return(out)
}
#=============================
# Kruskal-Wallis + Dunn (nonparam) (function)
kruskal_dunn_test <- function(var_list, daf){
  kruskal_df <- data.frame()
  kruskal_sig_df <- data.frame()
  dunn_df <- data.frame()
  dunn_sig_df <- data.frame()
  
  for(i in var_list)
  {
    ## tidy will summarise and return neat format
    a <- tidyr::tibble(kruskal_test(daf, daf[[i]] ~ groups))
    ## add variable name column
    a <- data.frame(variable = i, a)
    ## append to result df
    kruskal_df <- rbind(kruskal_df, a)
  }
  
  kruskal_sig_df <- kruskal_df %>% filter(p <= 0.05)
  
  ## dunn if kruskal sig
  
  ## check if kruskal sig not blank
  if (dim(kruskal_sig_df)[1] != 0){
    ## declare formula for dunn(rstatix)
    formulae <- lapply(kruskal_sig_df[,1], function(x) as.formula(paste0(x, " ~ groups")))
    ## apply games howell on welch sig column
    a <- lapply(formulae, function(x) dunn_test(x, data = daf,
                                                p.adjust.method = "holm", 
                                                detailed = FALSE))
    ## convert list to df
    dunn_df <- data.table::rbindlist(a)
    ## rename first column
    names(dunn_df)[1] <- "variable"
    ## filter significant games
    dunn_sig_df <- dunn_df %>% filter(p.adj.signif != 'ns') 
  } 
  out <- list(kruskal_df, kruskal_sig_df, dunn_df, dunn_sig_df)
  return(out)
}

#================================
# run omnibus test

if ('anova' %in% dist_var$omnibus) {
  ## run anova and tukey
  omni_anova_result <- anova_tukey_test(omni_anova, df)
  ## split list of df to df
  anova_df <- do.call(rbind.data.frame, omni_anova_result[1])
  anova_sig_df <- do.call(rbind.data.frame, omni_anova_result[2])
  tukey_df <- do.call(rbind.data.frame, omni_anova_result[3])
  tukey_sig_df <- do.call(rbind.data.frame, omni_anova_result[4])
}
#data.table::rbindlist(omni_anova_result[1])
if ('welch' %in% dist_var$omnibus) {
  ## run welch and games howell
  omni_welch_result <- welch_anova_games_test(omni_welch, df)
  ## split list of df to df
  welch_df <- do.call(rbind.data.frame, omni_welch_result[1])
  welch_sig_df <- do.call(rbind.data.frame, omni_welch_result[2])
  games_df <- do.call(rbind.data.frame, omni_welch_result[3])
  games_sig_df <- do.call(rbind.data.frame, omni_welch_result[4])
}

if ('nonparam' %in% dist_var$omnibus){
  ## run kruskal and dunn test
  omni_nonparam_result <- kruskal_dunn_test(omni_nonparam, df)
  ## split list of df to df
  kruskal_df <- do.call(rbind.data.frame, omni_nonparam_result[1])
  kruskal_sig_df <- do.call(rbind.data.frame, omni_nonparam_result[2])
  dunn_df <- do.call(rbind.data.frame, omni_nonparam_result[3])
  dunn_sig_df <- do.call(rbind.data.frame, omni_nonparam_result[4])
}

#================================
# make list of significant omnibus
columns <- c('variable','p')
var_sig_omni_df <- data.frame(matrix(nrow = 0, ncol = length(columns)))
colnames(var_sig_omni_df) = columns

if (dim(anova_sig_df)[1] != 0) {
  var_sig_omni_df <- rbind(var_sig_omni_df, anova_sig_df %>% select(variable, p, method))
}
if (dim(welch_sig_df)[1] != 0) {
  var_sig_omni_df <- rbind(var_sig_omni_df, welch_sig_df %>% select(variable, p, method))
}
if (dim(kruskal_sig_df)[1] != 0) {
  var_sig_omni_df <- rbind(var_sig_omni_df, kruskal_sig_df %>% select(variable, p, method))
}
# make list of not significant omnibus
var_not_sig_1omni <- var_name[!var_name %in% var_sig_omni_df[[1]]]
#or setdiff(var_name, var_sig_omni_df[[1]])
#================================
# combine pairwise result
pairwise_df <- data.frame()

merge_pairwise_result <- function(source_df) {
  merged_df <- data.frame()
  if (dim(source_df)[1] != 0) {
    #check if pairwise df still blank
    if (dim(pairwise_df)[1] == 0) {
      merged_df <- source_df %>% select(variable, group1, group2, p.adj) %>% spread(variable, p.adj)
    } else {
      #outer join pairwise df and source_d
      merged_df <- merge(x = pairwise_df, 
                       # select only 4 column, convert long to wide
                       y = source_df %>% select(variable, group1, group2, p.adj) %>% spread(variable, p.adj),
                       all = TRUE)
    }
  }
  # check if merged_df had been filled
  if (dim(merged_df)[1] !=0){
    return (merged_df)
  } else {return (pairwise_df)}
}

pairwise_df <- merge_pairwise_result(tukey_df)
pairwise_df <- merge_pairwise_result(dunn_df)
pairwise_df <- merge_pairwise_result(games_df)
#=======================================
# padjsignif merged (***, **, *, ns only. without number)
pairwise_df <- data.frame()

# combine pairwise result
merge_pairwise_result <- function(source_df) {
  merged_df <- data.frame()
  if (dim(source_df)[1] != 0) {
    #check if pairwise df still blank
    if (dim(pairwise_df)[1] == 0) {
      merged_df <- source_df %>% select(variable, group1, group2, p.adj.signif) %>% spread(variable, p.adj.signif)
    } else {
      #outer join pairwise df and source_d
      merged_df <- merge(x = pairwise_df, 
                         # select only 4 column, convert long to wide
                         y = source_df %>% select(variable, group1, group2, p.adj.signif) %>% spread(variable, p.adj.signif),
                         all = TRUE)
    }
  }
  # check if merged_df had been filled
  if (dim(merged_df)[1] !=0){
    return (merged_df)
  } else {return (pairwise_df)}
}

pairwise_df <- merge_pairwise_result(tukey_df)
pairwise_df <- merge_pairwise_result(dunn_df)
pairwise_df <- merge_pairwise_result(games_df)
#================================
# export to xlsx
dataset_names <- list('normality' =  normality_df,
                      'normality_sig' = normality_sig_df,
                      'homoscedasticity' = homoscedasticity_df,
                      'homoscedasticity_uev' = homoscedasticity_uev_df,
                      'dist_var' = dist_var,
                      'anova' = anova_df,
                      'anova_sig' = anova_sig_df,
                      'tukey' = tukey_df,
                      'tukey_sig' = tukey_sig_df,
                      'welch' = welch_df,
                      'welch_sig' = welch_sig_df,
                      'games' = games_df,
                      'games_sig' = games_sig_df,
                      'kruskal' = kruskal_df,
                      'kruskal_sig' = kruskal_sig_df,
                      'dunn' = dunn_df,
                      'dunn_sig' = dunn_sig_df,
                      'pairwise' = pairwise_df)

## export each data frame to separate sheets in same Excel file
openxlsx::write.xlsx(dataset_names, file = glue('output/{df_filename}_statistics.xlsx')) 

#================================
# create function for sig omni plot
plot_sig_omni <- function(xdf, sig_df, fun){
  ## check whether sig_df is not empty
  if (dim(sig_df)[1] != 0){
    ## loop over every var
    for (i in unique(sig_df$variable)){
      ## create formula to feed stat test
      formulae <- as.formula(glue("{i} ~ groups"))
      ## run post-hoc and add x y position for annotation
      stat.test <- xdf %>% fun(formulae) %>% add_xy_position()
      
      ## create plot with ggpubr
      bxp <- xdf %>% ggboxplot(x = "groups", y = as.character(i),
                              color = "black",
                              fill = "groups",
                              palette = NULL,
                              title = as.character(i),
                              xlab = "groups",
                              ylab = unit_df[[i]],
                              bxp.errorbar = TRUE,
                              bxp.errorbar.width = 0.1,
                              linetype = "solid",
                              size = NULL,
                              width = 0.7,
                              notch = FALSE,
                              outlier.shape = 19,
                              #add = "jitter",
                              #add.params = list(width = 0.1, color="black", size=2, alpha=0.4),
                              error.plot = "pointrange",
                              label = NULL,
                              font.label = list(size = 11, color = "black"),
                              ggtheme = scale_fill_viridis(discrete = TRUE, alpha=0.6, option = "viridis"))
      
      bxp <- bxp + geom_jitter(width = 0, color="black", size=2, alpha=0.4)
      
      bxp <- bxp +  theme(plot.title = element_text(hjust = 0.5, face="bold"), legend.position="none")#, tex
      
      bxp <- bxp + stat_pvalue_manual(stat.test, label = "p.adj.signif", tip.length = 0.01)
      
      ## export to pdf
      pdf(glue("output/pdf/{i}.pdf"))
      print(bxp)
      dev.off()
      
      ## export to hi-res png
      png(glue("output/png/{i}.png"), width = 2000, height = 2000, res=300)
      print(bxp)
      dev.off()
    }
  }
}

#================================

# create function for not sig omni plot
plot_not_sig_omni <- function(xdf, not_sig_l){
  ## check whether not sig list is not empty
  if (length(not_sig_l) != 0){
    ## loop over every var
    for (i in unique(not_sig_l)){
   
      ## create plot with ggpubr
      bxp <- xdf %>% ggboxplot(x = "groups", y = as.character(i),
                               color = "black",
                               fill = "groups",
                               palette = NULL,
                               title = as.character(i),
                               xlab = "groups",
                               ylab = unit_df[[i]],
                               bxp.errorbar = TRUE,
                               bxp.errorbar.width = 0.1,
                               linetype = "solid",
                               size = NULL,
                               width = 0.7,
                               notch = FALSE,
                               outlier.shape = 19,
                               #add = "jitter",
                               #add.params = list(width = 0.1, color="black", size=2, alpha=0.4),
                               error.plot = "pointrange",
                               label = NULL,
                               font.label = list(size = 11, color = "black"),
                               ggtheme = scale_fill_viridis(discrete = TRUE, alpha=0.6, option = "viridis"))
      
      bxp <- bxp + geom_jitter(width = 0, color="black", size=2, alpha=0.4)
      
      bxp <- bxp +  theme(plot.title = element_text(hjust = 0.5, face="bold"), legend.position="none")#, tex
      
      ## export to pdf
      pdf(glue("output/pdf/{i}.pdf"))
      print(bxp)
      dev.off()
      
      ## export to hi-res png
      png(glue("output/png/{i}.png"), width = 2000, height = 2000, res=300)
      print(bxp)
      dev.off()
    }
  }
}

#================================
# create function for graph only

plot_graph_only(df, var_name)
plot_graph_only <- function(xdf, var_name){
  for (i in var_name){
    formulae <- as.formula(glue("{i} ~ groups"))
    stat.test <- df %>%
      t_test(formulae) %>%
      adjust_pvalue(method = "bonferroni") %>%
      add_significance("p.adj") %>% add_xy_position()
    
    bxp <- xdf %>% ggboxplot(x = "groups", y = as.character(i),
                             color = "black",
                             fill = "groups",
                             palette = NULL,
                             title = as.character(i),
                             xlab = "groups",
                             ylab = unit_df[[i]],
                             bxp.errorbar = TRUE,
                             bxp.errorbar.width = 0.1,
                             linetype = "solid",
                             size = NULL,
                             width = 0.7,
                             notch = FALSE,
                             outlier.shape = 19,
                             #add = "jitter",
                             #add.params = list(width = 0.1, color="black", size=2, alpha=0.4),
                             error.plot = "pointrange",
                             label = NULL,
                             font.label = list(size = 11, color = "black"),
                             ggtheme = scale_fill_viridis(discrete = TRUE, alpha=0.6, option = "viridis"))
    
    bxp <- bxp + geom_jitter(width = 0, color="black", size=2, alpha=0.4)
    
    bxp <- bxp +  theme(plot.title = element_text(hjust = 0.5, face="bold"), legend.position="none")#, tex
    
    bxp <- bxp + stat_pvalue_manual(stat.test, label = "p.adj.signif", tip.length = 0.01)
    
    ## export to pdf
    pdf(glue("output/pdf/{i}.pdf"))
    print(bxp)
    dev.off()
    
    ## export to hi-res png
    png(glue("output/png/{i}.png"), width = 2000, height = 2000, res=300)
    print(bxp)
    dev.off()
  }
}

#===============
# plot for every sig
plot_sig_omni(df, tukey_sig_df, tukey_hsd)
plot_sig_omni(df, games_sig_df, games_howell_test)
plot_sig_omni(df, dunn_sig_df, dunn_test)

# plot for every not sig
plot_not_sig_omni(df, var_not_sig_omni)
#===============
cat('your files are in output folder')
stop()
exit()


