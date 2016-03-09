library(ggplot2)
library(reshape2)

#topic_names <- read.csv("../topic_names/final_lda20_fulltext.txt",header=FALSE,as.is=TRUE)
#topic_names <- read.csv("..//topic_names/abs_lda20_all4.txt",header=FALSE,as.is=TRUE)
#topic_names <- read.csv("~/work/tmpl/analysis/topic_names/abs_ICFP_lda20_topics.txt",header=FALSE,as.is=TRUE)


#src <- "2015-01-06_11:06_lda20.csv"
src <- "2016-03-06_14:40/lda25.csv"

setwd("~/tmpl/out/")
lda <- data.frame(read.csv(src, header=TRUE,sep=",",quote="\""))
#names(lda)[4:23] <- topic_names[1:20,]



# for OOP and OOSD
#s <- data.frame(c(lda[1:3],lda[16],lda[23]))
#names(s)[4:5] <- c(names(lda)[16],names(lda)[23])

# for languages and control
#s <- data.frame(c(lda[1:3],lda[10]))
#names(s)[4] <- names(lda)[10]

# PLDI data history stuff
#s <- data.frame(c(lda[1:3],lda[4],lda[8]))
#names(s)[4:5] <- c(names(lda)[4],names(lda)[8])

# POPL topics
#s <- data.frame(c(lda[1:3],lda[13],lda[22]))
#names(s)[4:5] <- c(names(lda)[13],names(lda)[22])

s <- data.frame(lda)

d <- melt(s,seq(1,3))
names(d)[4:5] <- c("Topic","Weight")

p <- ggplot(d, aes(x=Year,y=Weight,colour=Conference))
p + stat_smooth(method='loess')  + facet_wrap(~Topic) + theme(strip.text=element_text(size=10)) 
#coord_cartesian(ylim=c(-50,1100))
#+ coord_cartesian(ylim=c(-5,30)) 

# OOPSLA
# p + stat_smooth(method='loess') + coord_cartesian(ylim=c(-50,1100)) + facet_wrap(~Topic) + theme(strip.text=element_text(size=20))  + coord_cartesian(ylim=c(-5,30)) + geom_vline(xintercept=2006, colour = "green", linetype = "longdash") + geom_vline(xintercept=2010, colour = "red", linetype="longdash")


