#Vertex-based Timesync comparison confusion matrix viz

library(reshape2)
library(plyr)
library(ggplot2)
library(ggthemes)

### DEFINE MAIN DATA FRAME ######################

#flatten data function
flatten_confusion <- function(datapath, metric) {
  data=read.csv(datapath, header=T)
  df = melt(data)
  names(df) =  c('Timesync', 'LandTrendr', 'Frequency')
  df=subset(df, Frequency>=0) #get rid of timestamp row
  df$Plot = metric
  
  for (i in seq_len(nrow(df))){
    SPLIT = strsplit(toString(df$Timesync[i]), "_")
    df$TimesyncGroup[i] = sapply(SPLIT, "[", 1)
  }
  
  return(df)
}



#set working directory for new data & define datasets
setwd("/vol/v1/proj/timesync_validation/mr224_outputs/confusion_matrices/")

path_list = c("vertex_based/tsvalidation_detailedconfusion_mr224_vertvals_3x3_mean_v2_newbins_forestsonly.csv",
              "vertex_based/tsvalidation_detailedconfusion_mr224_vertvals_3x3_median_v2_newbins_forestsonly.csv")
metric_list = c("Mean", "Median")


#create one big data frame from all sources
big_df = NULL
for (i in seq_len(length(path_list))){
  big_df = rbind(big_df, flatten_confusion(path_list[i], metric_list[i]))
}


#DETERMINE LANDTRENDR GROUP

lt_disturbance = c( "X.1500_.250", "X.250_.50", "X.50_.5")
lt_stable = c("X.0.001_0.001", "X.5_.0.001", "X0.001_5")
lt_recovery = c("X5_50","X50_250")
 
addon <- c("LandTrendrGroup")
big_df[,addon] <- NA

for (i in seq_len(nrow(big_df))){
  if(big_df$LandTrendr[i] %in% lt_disturbance){
    big_df$LandTrendrGroup[i] <- "DISTURBANCE"} else if (big_df$LandTrendr[i] %in% lt_stable){
      big_df$LandTrendrGroup[i] <- "STABLE"
    } else if (big_df$LandTrendr[i] %in% lt_recovery){
      big_df$LandTrendrGroup[i] <- "RECOVERY"
    } else {
      big_df$LandTrendrGroup[i] <- "ERROR"
    }
}


#### NORMALIZE #################

#calc total frequency for each timesync group
flipTimesyncGroup <- function(df, metric){
  df$TotalVariable[i]<-"num_total"
  groups = dcast(df, TimesyncGroup ~ LandTrendrGroup, sum, value.var="Frequency", subset=.(Plot==metric))
  totals = dcast(df, TimesyncGroup ~ TotalVariable, sum, value.var="Frequency", subset=.(Plot==metric))
  names(totals) = c("TimesyncGroup", "Total")
  smalldf = cbind(groups,totals$Total)
  smalldf$Plot = metric
  names(smalldf) = c("TimesyncGroup", "DISTURBANCE", "RECOVERY", "STABLE", "Total", "Plot")
  
  
  return(smalldf)
  
}

tsgroups = NULL
for (i in metric_list){
  tsgroups <- rbind(tsgroups, flipTimesyncGroup(big_df, i))
}

plot_df = melt(tsgroups, id.var=c("TimesyncGroup","Plot", "Total"))
names(plot_df) = c("TimesyncGroup", "Plot", "Total", "LandTrendrGroup", "Frequency")

#determine if accuracy is true or false
for (i in seq_len(nrow(plot_df))){
  
  if (toString(plot_df$LandTrendrGroup[i]) == "RECOVERY"){
    
    if (toString(plot_df$TimesyncGroup[i]) == "RECOVERY"){
      plot_df$Accuracy[i] <- "True"
    } else {
      plot_df$Accuracy[i] <- "False"
    }
    
  } else if (toString(plot_df$LandTrendrGroup[i]) == "STABLE"){
    
    if(toString(plot_df$TimesyncGroup[i]) == "STABLE"){
      plot_df$Accuracy[i] <- "True"
    } else {
      plot_df$Accuracy[i] <- "False"
    }
      
  } else if (toString(plot_df$LandTrendrGroup[i]) == "DISTURBANCE"){
    
    if (toString(plot_df$TimesyncGroup[i]) == "RECOVERY"){
      plot_df$Accuracy[i] <- "False"
    } else if (toString(plot_df$TimesyncGroup[i]) == "STABLE"){
      plot_df$Accuracy[i] <- "False"
    } else {
      plot_df$Accuracy[i] = "True"
    }
  
  } else {
    plot_df$Accuracy[i] <- "Error"
    
  }
}
  
pal = palette(rainbow(2))
pal[2] = "#000000" #black
pal[1] = "#A9A9A9" #dark grey

plot_df$Percentage <- plot_df$Frequency/plot_df$Total * 100
ts_levels = rev(c("RECOVERY", "STABLE", "FIRE", "SITE-PREPARATION FIRE", "HARVEST", "MECHANICAL", "DELAY", "STRESS", "OTHER DISTURBANCE"))
lt_levels = c("DISTURBANCE", "STABLE", "RECOVERY")
acc_levels = c("True", "False")

MEAN = subset(plot_df, Plot=="Mean")
MEAN$LandTrendrGroup2<-factor(MEAN$LandTrendrGroup, levels=lt_levels)
MEAN$TimesyncGroup2<-factor(MEAN$TimesyncGroup, levels=ts_levels)
MEAN$Accuracy2<-factor(MEAN$Accuracy, levels=acc_levels)
p<-ggplot(MEAN)
p<-p+geom_point(aes(x=LandTrendrGroup2, y=TimesyncGroup2, size=Percentage, group=Accuracy, color=Accuracy, order=Accuracy2), pch=15)
p<-p+scale_color_manual(values=pal, guide=guide_legend(reverse=TRUE))
p<-p+scale_size_area(trans="identity",max_size=15)
p<-p+theme_tufte(base_size=15, base_family="BemboStd")
p<-p+xlab("LandTrendr")
p<-p+ylab("Timesync")
p<-p+ggtitle("Mean")
#p<-scale_x_discrete(limits=c("Disturbance", "Stable", "Recovery"))

MEDIAN = subset(plot_df, Plot=="Median")
MEDIAN$LandTrendrGroup2<-factor(MEDIAN$LandTrendrGroup, levels=lt_levels)
MEDIAN$TimesyncGroup2<-factor(MEDIAN$TimesyncGroup, levels=ts_levels)
MEDIAN$Accuracy2<-factor(MEDIAN$Accuracy, levels=acc_levels)
p2<-ggplot(MEDIAN)
p2<-p2+geom_point(aes(x=LandTrendrGroup2, y=TimesyncGroup2, size=Percentage, group=Accuracy, color=Accuracy), pch=15)
p2<-p2+scale_color_manual(values=pal, guide=guide_legend(reverse=TRUE))
p2<-p2+scale_size_area(trans="identity",max_size=15)
p2<-p2+theme_tufte(base_size=15, base_family="BemboStd")
p2<-p2+xlab("LandTrendr")
p2<-p2+ylab("Timesync")
p2<-p2+ggtitle("Median")


