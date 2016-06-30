#CONUS TIMESERIES CHARTS

# install.packages("ggplot2")
library(ggplot2)
#install.packages("plyr")
library(plyr)
#install.packages("ggthemes")
library(ggthemes)
#install.packages("extrafont")
library(extrafont)
#install.packages("grid")
#library(grid)

#set working directory for new data
setwd("/vol/v1/proj/timesync_validation/landtrendr_extraction_data/conus")

#read dataset
data=read.csv("conus_albers_nbr_3x3kernel_allmetrics_summary_withraw_1986_2012.csv", header = T)

#get list of unique ids
uids = unique(data$UID)

#uid = uids[1]

#set plot parameters
xrange = c(1985,2013)
ranges=data.frame(xrange)
colnames(ranges)[1] = "X"

#color scheme
processes = levels(data$CHANGE_PROCESS)
colors = c("red", "red", "steelblue", "red", "red", "red", "red", "steelblue", "green4", "red", "steelblue", "orange", "red", "red")

#loop thru unique ids & plot them

#plots<-c()
setwd("/vol/v1/proj/timesync_validation/validation_outputs/conus/charts")
pdf("all_conus_nbr_albers_forest_plots_targetday_3x3center_fixedinterp.pdf")
for(uid in uids){
  
  sub = subset(data, UID==uid)
  
  #y_max = max(max(sub$NBR_SCALED_TARGET), max(sub$FLIP_FTV))
  y_max = max(max(sub$NBR_SCALED_TARGET), max(sub$MID_PIX_VERTVALS))
  
  p<-ggplot(sub)
  #p<-p+geom_line(aes(x=YEAR, y=FLIP_FTV), lwd=1.5, col="blue")
  p<-p+geom_line(aes(x=YEAR, y=MID_PIX_VERTVALS), lwd=1.5, col="blue")
  p<-p+geom_point(aes(x=YEAR, y=NBR_SCALED_TARGET), col="black")
  p<-p+geom_text(aes(x=YEAR, y=y_max+40, label=CHANGE_PROCESS, color=CHANGE_PROCESS), size=4, angle=50)
  p<-p+scale_color_manual(values=colors, limits=processes)
  #p<-p+geom_line(y=sub$NBR_SCALED_MEAN, lwd=1.5)
  #p<-p+geom_line(aes(x=DataSource, y=Accuracy), linetype="l", pch=16, lwd=.5, lty=1, col="black")
  p<-p+theme(axis.text.x=element_text(size=rel(2),vjust=0.45))
  p<-p+theme(axis.text.y=element_text(size=rel(2)))
  p<-p+theme(plot.title=element_text(lineheight=0.7, size=rel(2)))
  p<-p+scale_x_continuous(limits=xrange)
  p<-p+ylab('NBR')
  p<-p+theme_tufte(base_size=12, base_family="Helvetica")
  p<-p+theme(legend.position="none")
  p<-p+ggtitle(uid)
  
  #plots<-c(plots,p)
  print(p)
}

dev.off()
#pdf("all.pdf")
#invisible(lapply(plots, print))
#dev.off()

#ggsave("arrange2x2.pdf", marrangeGrob(grobs=1, nrow=2, ncol=2))


