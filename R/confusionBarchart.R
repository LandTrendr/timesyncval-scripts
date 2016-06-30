#3 stacked bar charts: True Positives, False Negatives, False Positives
#True Negatives cannot be included
#this will include all event-based data

#Fill=Data source (GD/GFD/Vertvals, etc)
#x-axis=Timesync categories
#y-axis=frequency

#DEFINE MAIN DATA FRAME

#Real data

#set working directory for new data
setwd("/vol/v1/proj/timesync_validation/mr224_outputs/confusion_matrices/")

`%notin%` <- function(x,y) !(x %in% y) 

#GREATEST DISTURBANCE - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_mean_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gdmean=melt(data)

names(df_gdmean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmean$Plot = "Mean"
df_gdmean$DataSource = "Greatest Disturbance"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gdmean$Total[df_gdmean$Timesync==i] <- totals[iter]
  iter = iter+1
}



#GREATEST DISTURBANCE - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_median_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gdmedian=melt(data)

names(df_gdmedian) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmedian$Plot = "Median"
df_gdmedian$DataSource = "Greatest Disturbance"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gdmedian$Total[df_gdmedian$Timesync==i] <- totals[iter]
  iter = iter+1
}

#GREATEST FAST DISTURBANCE - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances/tsvalidation_detailedconfusion_mr224_gfd_2gfd_3x3_mean_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gfdmean=melt(data)

names(df_gfdmean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmean$Plot = "Mean"
df_gfdmean$DataSource = "Greatest Fast Disturbance"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gfdmean$Total[df_gfdmean$Timesync==i] <- totals[iter]
  iter = iter+1
}

#GREATEST FAST DISTURBANCE - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances/tsvalidation_detailedconfusion_mr224_gfd_2gfd_3x3_median_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gfdmedian=melt(data)

names(df_gfdmedian) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmedian$Plot = "Median"
df_gfdmedian$DataSource = "Greatest Fast Disturbance"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gfdmedian$Total[df_gfdmedian$Timesync==i] <- totals[iter]
  iter = iter+1
}

#GREATEST DISTURBANCE MMU11 - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_mean_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gdmmu11mean=melt(data)

names(df_gdmmu11mean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmmu11mean$Plot = "Mean"
df_gdmmu11mean$DataSource = "Greatest Disturbance MMU11 Tight"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gdmmu11mean$Total[df_gdmmu11mean$Timesync==i] <- totals[iter]
  iter = iter+1
}

#GREATEST DISTURBANCE MMU11 - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_median_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gdmmu11median=melt(data)

names(df_gdmmu11median) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmmu11median$Plot = "Median"
df_gdmmu11median$DataSource = "Greatest Disturbance MMU11 Tight"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gdmmu11median$Total[df_gdmmu11median$Timesync==i] <- totals[iter]
  iter = iter+1
}

#GREATEST FAST DISTURBANCE MMU11 - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gfd_2gfd_mmu11_tight_3x3_mean_forestsonly_compressed.csv", header=T)

#calculate total frequency for each timesync class
totals = c()
classes = levels(data$X)
columns = colnames(data)[colnames(data) %notin% c("X","Total")]
for (i in seq_len(nrow(data))){
  totals[i] <- sum(data[i,columns])
}

#flatten data
df_gfdmmu11mean=melt(data)

names(df_gfdmmu11mean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmmu11mean$Plot = "Mean"
df_gfdmmu11mean$DataSource = "Greatest Fast Disturbance MMU11 Tight"

#GREATEST FAST DISTURBANCE MMU11- MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gfd_2gfd_mmu11_tight_3x3_median_forestsonly_compressed.csv", header=T)

#flatten data
df_gfdmmu11median=melt(data)

names(df_gfdmmu11median) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmmu11median$Plot = "Median"
df_gfdmmu11median$DataSource = "Greatest Fast Disturbance MMU11 Tight"

#attach totals to data frame
iter = 1
for (i in classes){
  df_gfdmmu11median$Total[df_gfdmmu11median$Timesync==i] <- totals[iter]
  iter = iter+1
}

#combine all datasets
big_df = rbind(df_gdmean, df_gdmedian, df_gfdmean, df_gfdmedian, df_gdmmu11mean, df_gdmmu11median, df_gfdmmu11mean, df_gfdmmu11median)

#DETERMINE CHART CONFUSION GROUP

timesync_pos = c("FIRE_1", "FIRE_2", "FIRE_3", "HARVEST_0", "HARVEST_1", "HARVEST_2", "HARVEST_3", "HARVEST_SITE-PREPARATION FIRE", "MECHANICAL_1", "OTHER DISTURBANCE_1", "OTHER DISTURBANCE_2", "SITE-PREPARATION FIRE_1", "STRESS_1", "STRESS_2")
timesync_neg = c("RECOVERY_0", "STABLE_0")
landtrendr_pos = c("X10_20", "X20_30", "X30_40", "X40_50", "X50_60", "X60_70", "X70_80", "X80_90", "X90_100", "X100_200")
landtrendr_neg = c("X0_1", "X1_4", "X4_10")

addon <- c("Confusion")
big_df[,addon] <- NA

for (i in seq_len(nrow(big_df))){
  if( (big_df$Timesync[i] %in% timesync_pos) & (big_df$LandTrendr[i] %in% landtrendr_pos) ){
    big_df$Confusion[i] <- "True Positive"
  } else if ((big_df$Timesync[i] %in% timesync_pos) & (big_df$LandTrendr[i] %in% landtrendr_neg)){
    big_df$Confusion[i] <- "False Negative"
  } else if ((big_df$Timesync[i] %in% timesync_neg) & (big_df$LandTrendr[i] %in% landtrendr_pos)){
    big_df$Confusion[i] <- "False Positive"
  } else {
    big_df$Confusion[i] <- "ERROR"
  }
}

#separate median & mean groups
mean_df = subset(big_df, Plot=="Mean")
median_df = subset(big_df, Plot=="Median")

# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)
  
  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)
  
  numPlots = length(plots)
  
  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                     ncol = cols, nrow = ceiling(numPlots/cols))
  }
  
  if (numPlots==1) {
    print(plots[[1]])
    
  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))
    
    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))
      
      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

yrange = c(0,15)

TP = subset(median_df, Confusion=="True Positive")
p1<-ggplot()
p1<-p1+geom_bar(aes(Timesync, Frequency, fill=DataSource, order=DataSource), TP, stat="identity", position="dodge")
p1<-p1+theme_tufte(base_size=20, base_family="BemboStd")
p1<-p1+theme(axis.text.x=element_text(angle=90, size=rel(.75), vjust=0.45))
#p1<-p1+theme(legend.title=element_text(size=rel(0.5)))
#p1<-p1+theme(legend.text=element_text(size=rel(0.5)))
p1<-p1+theme(legend.position = "none")
p1<-p1+scale_fill_grey()
p1<-p1+scale_y_continuous(limits=yrange)
p1<-p1+ggtitle("True Positive")

FP = subset(median_df, Confusion=="False Positive")
p2<-ggplot()
p2<-p2+geom_bar(aes(Timesync, Frequency, fill=DataSource, order=DataSource), FP, stat="identity", position="dodge")
p2<-p2+theme_tufte(base_size=20, base_family="BemboStd")
p2<-p2+theme(axis.text.x=element_text(angle=90, size=rel(.75), vjust=0.45))
p2<-p2+theme(legend.title=element_text(size=rel(0.75)))
p2<-p2+theme(legend.text=element_text(size=rel(0.75)))
#p2<-p2+theme(legend.position = "none")
p2<-p2+scale_x_discrete(limits=unique(FP$Timesync), labels=c("                                  RECOVERY", "                                  STABLE"))
p2<-p2+scale_fill_grey()
p2<-p2+scale_y_continuous(limits=yrange)
p2<-p2+ggtitle("False Positive")
p2<-p2+ylab("")

FN = subset(median_df, Confusion=="False Negative")
p3<-ggplot()
p3<-p3+geom_bar(aes(Timesync, Frequency/Total, fill=DataSource, order=DataSource), FN, stat="identity", position="dodge")
p3<-p3+theme_tufte(base_size=20, base_family="BemboStd")
p3<-p3+theme(axis.text.x=element_text(angle=90, size=rel(.75), vjust=0.45))
#p1<-p1+theme(legend.title=element_text(size=rel(0.5)))
#p1<-p1+theme(legend.text=element_text(size=rel(0.5)))
p3<-p3+theme(legend.position = "none")
p3<-p3+scale_fill_grey()
p3<-p3+ggtitle("False Negative")
p3<-p3+scale_y_continuous(limits=yrange)
p3<-p3+ylab("")

