require(ggplot2)

setwd("~/r/snapl/citations")
unified <- data.frame(read.csv("dist_rand.dat",header=TRUE))
p <- ggplot(subset(unified,Type!="paper"),aes(x=factor(Paper),y=Distance))
p + geom_boxplot(aes(colour=factor(Type))) + scale_x_discrete(label=c("CDRS","PCC","SEMC","TAL")) + scale_colour_discrete(label=c("Citations","Random 1","Random 2","Random 3","Random 4","Random 5")) + labs(x="Paper",colour="Paper set")
