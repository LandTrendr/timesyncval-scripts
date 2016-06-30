##Multi-dimensional confusion matrix visualization
##TESTING!
##
##Author: Tara Larrue

library(reshape2)

#Test data
#countries = c('IND', 'AUS', 'CHI', 'JAP', 'BAT', 'SING')
#frequencies = matrix(sample(1:100, 36), 6, 6, dimnames=list(countries,countries))
#frequencies2 = matrix(sample(1:100, 36), 6, 6, dimnames=list(countries,countries))
#diag(frequencies) = 0
#diag(frequencies2) = 0

#frequencies_df = melt(frequencies)
#frequencies2_df = melt(frequencies2)

#names(frequencies_df) = c('origin', 'destination', 'frequency')
#names(frequencies2_df) = c('origin', 'destination', 'frequency')

#frequencies_df$source = "gd"
#frequencies_df$offset_x = -0.1
#frequencies_df$offset_y = 0.1

#frequencies2_df$source = "gfd"
#frequencies2_df$offset_x = 0.1
#frequencies2_df$offset_y = -0.1

#both_df = rbind(frequencies_df, frequencies2_df)

#order
#fake_coords= c(1,2,3,4,5,6)
#xlabels=countries
#ylabels=countries

#both_df$x[both_df$origin=="IND"]<-1
#both_df$x[both_df$origin=="AUS"]<-2
#both_df$x[both_df$origin=="CHI"]<-3
#both_df$x[both_df$origin=="JAP"]<-4
#both_df$x[both_df$origin=="BAT"]<-5
#both_df$x[both_df$origin=="SING"]<-6
#both_df$y[both_df$destination=="IND"]<-1
#both_df$y[both_df$destination=="AUS"]<-2
#both_df$y[both_df$destination=="CHI"]<-3
#both_df$y[both_df$destination=="JAP"]<-4
#both_df$y[both_df$destination=="BAT"]<-5
#both_df$y[both_df$destination=="SING"]<-6
################################

#Real data

#set working directory for new data
setwd("/vol/v1/proj/timesync_validation/mr224_outputs/confusion_matrices/")

#GREATEST DISTURBANCE - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_mean_forestsonly_compressed.csv", header=T)

#flatten data
df_gdmean=melt(data)

names(df_gdmean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmean$Plot = "Mean"
df_gdmean$DataSource = "Greatest Disturbance"

#GREATEST DISTURBANCE - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances/tsvalidation_detailedconfusion_mr224_gd_2gd_3x3_median_forestsonly_compressed.csv", header=T)

#flatten data
df_gdmedian=melt(data)

names(df_gdmedian) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmedian$Plot = "Median"
df_gdmedian$DataSource = "Greatest Disturbance"

#GREATEST FAST DISTURBANCE - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances/tsvalidation_detailedconfusion_mr224_gfd_2gfd_3x3_mean_forestsonly_compressed.csv", header=T)

#flatten data
df_gfdmean=melt(data)

names(df_gfdmean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmean$Plot = "Mean"
df_gfdmean$DataSource = "Greatest Fast Disturbance"

#GREATEST FAST DISTURBANCE - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances/tsvalidation_detailedconfusion_mr224_gfd_2gfd_3x3_median_forestsonly_compressed.csv", header=T)

#flatten data
df_gfdmedian=melt(data)

names(df_gfdmedian) = c('Timesync', 'LandTrendr', 'Frequency')
df_gfdmedian$Plot = "Median"
df_gfdmedian$DataSource = "Greatest Fast Disturbance"

#GREATEST DISTURBANCE MMU11 - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_mean_forestsonly_compressed.csv", header=T)

#flatten data
df_gdmmu11mean=melt(data)

names(df_gdmmu11mean) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmmu11mean$Plot = "Mean"
df_gdmmu11mean$DataSource = "Greatest Disturbance MMU11 Tight"

#GREATEST DISTURBANCE MMU11 - MEDIAN
#read confusion matrix
data=read.csv("eventbased_greatest_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gd_2gd_mmu11_tight_3x3_median_forestsonly_compressed.csv", header=T)

#flatten data
df_gdmmu11median=melt(data)

names(df_gdmmu11median) = c('Timesync', 'LandTrendr', 'Frequency')
df_gdmmu11median$Plot = "Median"
df_gdmmu11median$DataSource = "Greatest Disturbance MMU11 Tight"

#GREATEST FAST DISTURBANCE MMU11 - MEAN
#read confusion matrix
data=read.csv("eventbased_greatest_fast_disturbances_filtered/tsvalidation_detailedconfusion_mr224_gfd_2gfd_mmu11_tight_3x3_mean_forestsonly_compressed.csv", header=T)

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


#combine all datasets
big_df = rbind(df_gdmean, df_gdmedian, df_gfdmean, df_gfdmedian, df_gdmmu11mean, df_gdmmu11median, df_gfdmmu11mean, df_gfdmmu11median)

#determine grid parameters from lookup table

#define xoffset lookup table
lookupValue = c("Greatest Disturbance", "Greatest Fast Disturbance", "Greatest Disturbance MMU11 Tight", "Greatest Fast Disturbance MMU11 Tight")
lookupVariable = rep("DataSource",4)
newVariable = rep("Xoffset",4)
newValue = c(-.1, .1, -.1, .1)
lookupTable_xoffset = data.frame(lookupVariable, lookupValue, newVariable, newValue)

#define yoffset lookup table
lookupValue = c("Greatest Disturbance", "Greatest Fast Disturbance", "Greatest Disturbance MMU11 Tight", "Greatest Fast Disturbance MMU11 Tight")
lookupVariable = rep("DataSource",4)
newVariable = rep("Yoffset",4)
newValue = c(.1, .1, -.1, -.1)
lookupTable_yoffset=data.frame(lookupVariable, lookupValue, newVariable, newValue)

#define x lookup table

#order lantrendr groups by ordering upper range integers
ints = c()
for (i in strsplit(levels(big_df$LandTrendr), "_")){
  ints <- c(ints, strtoi(i[2]))
}

values = levels(big_df$LandTrendr)[order(ints)]
numLandTrendr = length(values)

lookupValue = values
newValue = seq(1,numLandTrendr)
lookupVariable <- rep("LandTrendr", numLandTrendr)
newVariable <- rep("X", numLandTrendr)
lookupTable_x=data.frame(lookupVariable, lookupValue, newVariable, newValue)

#define y lookup table
numTimesync = length(levels(big_df$Timesync))
lookupValue = levels(big_df$Timesync)
newValue = seq(1,numTimesync) #don't worry about order of timesync groups for now
lookupVariable <-rep("Timesync",numTimesync)
newVariable <- rep("Y",numTimesync)
lookupTable_y=data.frame(lookupVariable, lookupValue, newVariable, newValue)

addNewData <- function(import, data){
  
  for (i in seq_len(nrow(import))){
    
    to = import$newVariable[i]
    from = import$lookupVariable[i]

    old = import$lookupValue[i]
    new = import$newValue[i]
    
    if (i==1){
      addon <- c(toString(to))
      data[,addon] <- NA
    }
    
    data[,addon][data[,toString(from)]==toString(old)] <- new

  }
  
  return(data)
  
}

big_df = addNewData(lookupTable_y, big_df)
big_df = addNewData(lookupTable_x, big_df)
big_df <- addNewData(lookupTable_yoffset, big_df)
big_df <- addNewData(lookupTable_xoffset, big_df)

library(ggplot2)
library(ggthemes)
dodge1 <- position_dodge(width=0.1)
#dodge2 <- position_dodge(width=-0.5)
#dodge3 <- position_dodge(width=0.5, height=-0.5)
#dodge4 <- position_dodge(width=-0.5, height=-0.5)


# p<-ggplot(both_df, (aes(color=source, group=source))) 
# p<-p+geom_point(data=subset(both_df, source=="gd"), aes(x=x+offset_x, y=y+offset_y, size=frequency),pch=15)
# p<-p+scale_x_discrete(breaks=fake_coords, labels=xlabels)
# p<-p+scale_y_discrete(breaks=fake_coords, labels=ylabels)

lt_labels = c("0-0.9","1-3.9", "4-9.9", "10-19.9", "20-29.9", "30-39.9", "40-49.9","50-59.9", "60-69.9", "70-79.9", "80-89.9", "90-99.9", "100-above")
p<-ggplot(big_df, (aes(color=DataSource, group=DataSource))) 
p<-p+geom_point(aes(x=X+Xoffset, y=Y+Yoffset, size=Frequency), pch=15)
p<-p+scale_x_discrete(breaks=sort(unique(big_df$X)), labels=lt_labels)
p<-p+scale_y_discrete(breaks=sort(unique(big_df$Y)), labels=levels(big_df$Timesync))
p<-p+scale_color_grey()
p<-p+scale_size_area(max_size=8)
p<-p+theme_tufte(base_size=15, base_family="BemboStd")
p<-p+xlab("LandTrendr")
p<-p+ylab("Timesync")

#get size of points from ggplot's internal data
library(grid)
g = ggplot_build(p)
big_df$size = g$data[[1]]$size
big_df$offset = sqrt(big_df$size)

#recalculate offsets

#define xoffset
big_df$Xoffset[big_df$DataSource=="Greatest Disturbance"] = unit(big_df$offset[big_df$DataSource=="Greatest Disturbance"]*-1, "pt")
big_df$Xoffset[big_df$DataSource=="Greatest Fast Disturbance"] = unit(big_df$offset[big_df$DataSource=="Greatest Fast Disturbance"], "pt")
big_df$Xoffset[big_df$DataSource=="Greatest Disturbance MMU11 Tight"] = unit(big_df$offset[big_df$DataSource=="Greatest Disturbance MMU11 Tight"]*-1,"pt")
big_df$Xoffset[big_df$DataSource=="Greatest Fast Disturbance MMU11 Tight"] = unit(big_df$offset[big_df$DataSource=="Greatest Fast Disturbance MMU11 Tight"],"pt")

#define yoffset
big_df$Yoffset[big_df$DataSource=="Greatest Disturbance"] = big_df$offset[big_df$DataSource=="Greatest Disturbance"]
big_df$Yoffset[big_df$DataSource=="Greatest Fast Disturbance"] = big_df$offset[big_df$DataSource=="Greatest Fast Disturbance"]
big_df$Yoffset[big_df$DataSource=="Greatest Disturbance MMU11 Tight"] = big_df$offset[big_df$DataSource=="Greatest Disturbance MMU11 Tight"]*-1
big_df$Yoffset[big_df$DataSource=="Greatest Fast Disturbance MMU11 Tight"] = big_df$offset[big_df$DataSource=="Greatest Fast Disturbance MMU11 Tight"]*-1

p2<-ggplot(big_df, (aes(color=DataSource, group=DataSource)))
#xx = as.data.frame(subset(big_df, big_df$Plot=="Mean")$X)
#yy = as.data.frame(subset(big_df, big_df$Plot=="Mean")$Y)
print(unit(big_df$X,"native"))
print(unit(big_df$Y,"native"))
grid.points(x=unit(big_df$X,"native")+unit(big_df$Xoffset,"pt"), y=unit(big_df$Y,"native")+unit(big_df$Yoffset,"pt"), pch=15, default.units="native")

#p2<-p2+geom_point(aes(x=unit(big_df$X,"native"), y=unit(big_df$Y,"native"), size=Frequency), pch=15)
#p2<-p2+scale_x_discrete(breaks=sort(unique(big_df$X)), labels=lt_labels)
#p2<-p2+scale_y_discrete(breaks=sort(unique(big_df$Y)), labels=levels(big_df$Timesync))




#p<-p+geom_point(aes(x=origin, y=destination, size=frequency), pch=15, position=dodge1)
#p<-p+geom_jitter(aes(x=origin, y=destination, size=frequency), width=0.3, height=0.3)
#p<-p+geom_jitter(data=subset(both_df, source=="gd"), aes(x=origin, y=destination, size=frequency), pch=15)
#p<-p+geom_jitter(data=subset(both_df, source=="gfd"), aes(x=origin, y=destination, size=frequency), pch=15)
p2<-p2+scale_color_grey()
p2<-p2+scale_size_area(max_size=8)
p2<-p2+theme_tufte(base_size=15, base_family="BemboStd")
p2<-p2+xlab("LandTrendr")
p2<-p2+ylab("Timesync")

#axis(1,labels=both_df$origin)
p
#aes(x=origin, y=destination, size=frequency, color="grey")) + geom_point()
#p<-p + ggplot(frequencies2_df, aes(x=origin, y=destination, size=frequency, color="black")) + geom_point()
#p
