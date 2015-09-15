library(ggplot2)
library(reshape2)

topic_names <- read.csv("../topic_names/final_lda20_fulltext.txt",header=FALSE,as.is=TRUE)

src <- "fulltext_lda20.csv"

lda <- data.frame(read.csv(src, header=TRUE,sep=",",quote="\""))
names(lda)[4:23] <- topic_names[1:20,]

d <- melt(lda,seq(1,3))
names(d)[4:5] <- c("Topic","Weight")

p <- ggplot(d, aes(x=Topic,y=Weight,fill=Conference))
p + geom_bar(stat="identity", position="dodge") + theme(strip.text=element_text(size=10), axis.text.x=element_text(angle=90)) 
