#Line Graphs for each Timesync class showing progression from Vertvals -> GD -> GD MMU11

library(reshape2)
library(ggplot2)
library(plyr)
library(ggthemes)

### DEFINE MAIN DATA FRAME ######################

#set working directory for new data
setwd("/vol/v1/proj/timesync_validation/mr224_outputs/confusion_matrices/")

`%notin%` <- function(x,y) !(x %in% y) 

#flatten data function
flatten_confusion <- function(datapath, metric, datasource) {
  data=read.csv(datapath, header=T)
  df = melt(data)
  names(df) =  c('Timesync', 'LandTrendr', 'Frequency')
  df=subset(df, Frequency>=0) #get rid of timestamp row
  df$Plot = metric
  df$DataSource = datasource
  
  for (i in seq_len(nrow(df))){
    SPLIT = strsplit(toString(df$Timesync[i]), "_")
    df$TimesyncGroup[i] = sapply(SPLIT, "[", 1)
  }
 
  return(df)
}


#define confusion matrices to read
path_list = c("eventbased_vertvals/tsvalidation_detailedconfusion_mr224_vertvals_3x3_median_events_forestsonly.csv",
              "eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_median_forestsonly_compressed.csv",
              "eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_median_forestsonly_compressed.csv",
              "eventbased_vertvals/tsvalidation_detailedconfusion_mr224_vertvals_3x3_mean_events_forestsonly.csv",
              "eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_mean_forestsonly_compressed.csv",
              "eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_mean_forestsonly_compressed.csv")

source_list = c("Fitted Imagery", "Greatest Disturbance", "Greatest Disturbance MMU11 Tight", 
                "Fitted Imagery", "Greatest Disturbance", "Greatest Disturbance MMU11 Tight")

metric_list = c("Median", "Median", "Median", "Mean", "Mean", "Mean")

#create one big data frame from all sources
df = NULL
for (i in seq_len(length(path_list))){
  df = rbind(df, flatten_confusion(path_list[i], metric_list[i], source_list[i]))
}

### POPULATE NECESSARY COLUMNS #################

#define which categories are considered disturbane/non-disturbance
ts_disturbance = c("FIRE_1", "FIRE_2", "FIRE_3", "HARVEST_0", "HARVEST_1", "HARVEST_2", "HARVEST_3", "HARVEST_SITE-PREPARATION FIRE", "MECHANICAL_1", "OTHER DISTURBANCE_1", "OTHER DISTURBANCE_2", "SITE-PREPARATION FIRE_1", "STRESS_1", "STRESS_2")
ts_non = c("RECOVERY_0", "STABLE_0")
lt_disturbance = c("X10_20", "X20_30", "X30_40", "X40_50", "X50_60", "X60_70", "X70_80", "X80_90", "X90_100", "X100_200", "X.1500_.250", "X.250_.50", "X.50_.10")
lt_non = c("X0_1", "X1_4", "X4_10", "X.1500_.250", "X.250_.50", "X.10_.5", "X.5_.0.001", "X0.001_5", "X5_10", "X10_50", "X50_250")

#populate num_true column
temp_df = df
for (i in seq_len(nrow(temp_df))){
  temp_df$TotalVariable[i]<-"num_total"
  temp_df$TrueVariable[i]<-"num_true"
  if( (temp_df$LandTrendr[i] %in% lt_disturbance) & (temp_df$Timesync[i] %in% ts_disturbance) ){
    temp_df$TrueValue[i] <- temp_df$Frequency[i]
  }
  else if((temp_df$LandTrendr[i] %in% lt_non) & (temp_df$Timesync[i] %in% ts_non)){
    temp_df$TrueValue[i] <- temp_df$Frequency[i]
  }
  else{
    temp_df$TrueValue[i] <- 0
  }
}


#flip data so Timesync is unique id
flipTimesync <- function(df, datasource){
  true_totals = dcast(df, Timesync + Plot ~ TrueVariable, sum, value.var="TrueValue", subset=.(DataSource==datasource))
  all_totals = dcast(df, Timesync + Plot ~ TotalVariable, sum, value.var="Frequency", subset=.(DataSource==datasource))
  smalldf = cbind(true_totals,all_totals[,2])
  names(smalldf) = c("Timesync", "Plot", "True", "Total")
  smalldf$Accuracy = as.numeric(smalldf$True)/as.numeric(smalldf$Total)
  smalldf$DataSource = datasource
  
  return(smalldf)
}

flipTimesyncGroup <- function(df, datasource){
  true_totals = dcast(df, TimesyncGroup + Plot ~ TrueVariable, sum, value.var="TrueValue", subset=.(DataSource==datasource))
  all_totals = dcast(df, TimesyncGroup + Plot ~ TotalVariable, sum, value.var="Frequency", subset=.(DataSource==datasource))
  smalldf = cbind(true_totals,all_totals$num_total)
  print(smalldf)
  names(smalldf) = c("TimesyncGroup", "Plot", "True", "Total")
  smalldf$Accuracy = as.numeric(smalldf$True)/as.numeric(smalldf$Total)
  smalldf$DataSource = datasource
  
  return(smalldf)
}

smalldfs = NULL
for (i in source_list){
  smalldfs <- rbind(smalldfs, flipTimesync(temp_df,i))
}

smalldfs_group = NULL
for (i in source_list){
  smalldfs_group <- rbind(smalldfs_group, flipTimesyncGroup(temp_df,i))
}



#### PLOT DATA ####################################

#function to define a plot
defineplot <- function(tsnames) {
  h<-ggplot(subset(smalldfs, Timesync %in% tsnames))+
    geom_line(aes(x=DataSource, y=Accuracy), lwd=.75, lty=1, color=tsnames)+
    #geom_line(aes(y=Min), linetype="l", pch=16, lwd=.5, lty=1, col="lightgrey")+
    #geom_line(aes(y=Max), linetype="l", pch=16, lwd=.5, lty=1, col="lightgrey")+
    #geom_line(aes(y=Median), type="l", pch=16, lwd=.75, lty=1, col="black")+
    #ggtitle(tsname)+
    #theme(axis.text.x=element_text(angle=90.,size=rel(2),vjust=0.45))+
    theme(axis.text.x=element_text(size=rel(2),vjust=0.45))+
    theme(axis.text.y=element_text(size=rel(2)))+
    theme(plot.title=element_text(lineheight=0.7, size=rel(2)))+
    #scale_y_continuous(limits=yrange, breaks=seq(-5,5,1))+p
    #scale_x_continuous(limits=c(1991,2010), breaks=seq(1990,2010,5))+
    #geom_rangeframe(aes(y=Min))+
    #geom_rangeframe(data=ranges, mapping=aes(x=X, y=Y))+
    theme_tufte(base_size=20, base_family="BemboStd")
  
  return(h)
}

yrange = c(0.,1.)
ranges=data.frame(yrange)
colnames(ranges)[1] = "Y"

plot_list = c("FIRE", "HARVEST", "MECHANICAL", "OTHER DISTURBANCE", "SITE-PREPARATION FIRE", "STRESS")
sub = subset(smalldfs_group, Plot=="Median")
sub = subset(sub, TimesyncGroup %in% plot_list)
p<-ggplot(sub, aes(x=DataSource, y=Accuracy, group=TimesyncGroup, color=TimesyncGroup))
p<-p+geom_line(lwd=1.5)
#p<-p+geom_line(aes(x=DataSource, y=Accuracy), linetype="l", pch=16, lwd=.5, lty=1, col="black")
p<-p+theme(axis.text.x=element_text(size=rel(2),vjust=0.45))
p<-p+theme(axis.text.y=element_text(size=rel(2)))
p<-p+theme(plot.title=element_text(lineheight=0.7, size=rel(2)))
p<-p+scale_y_continuous(limits=yrange)
p<-p+theme_tufte(base_size=20, base_family="BemboStd")
p<-p+ggtitle("Median")
#p<-p+geom_rangeframe(data=ranges, mapping=aes(y=Y))

sub = subset(smalldfs_group, Plot=="Mean")
print(sub)
sub = subset(sub, TimesyncGroup %in% plot_list)
p2<-ggplot(sub, aes(x=DataSource, y=Accuracy, group=TimesyncGroup, color=TimesyncGroup))
p2<-p2+geom_line(lwd=1.5)
#p<-p+geom_line(aes(x=DataSource, y=Accuracy), linetype="l", pch=16, lwd=.5, lty=1, col="black")
p2<-p2+theme(axis.text.x=element_text(size=rel(2),vjust=0.45))
p2<-p2+theme(axis.text.y=element_text(size=rel(2)))
p2<-p2+theme(plot.title=element_text(lineheight=0.7, size=rel(2)))
p2<-p2+scale_y_continuous(limits=yrange)
p2<-p2+theme_tufte(base_size=20, base_family="BemboStd")
p2<-p2+ggtitle("Mean")

  
              