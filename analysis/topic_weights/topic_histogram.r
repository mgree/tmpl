library(ggplot2)
library(reshape2)
library(dplyr) # run install.packages('dplyr') to get this

topic_names <- read.csv("../topic_names/abs_ICFP_lda20_topics.txt",header=FALSE,as.is=TRUE)

src <- "../../out/2015-08-26_19:30/lda20.csv"

lda <- data.frame(read.csv(src, header=TRUE,sep=",",quote="\""))
names(lda)[4:23] <- topic_names[1:20,]

d <- melt(lda,seq(1,3))
names(d)[4:5] <- c("Topic","Weight")

# thanks to Noam Ross for the tip onin using dplyr/this bit of code
d2 = d %>% group_by(Topic, Conference) %>% summarize(Total = sum(Weight))

p <- ggplot(d2, aes(x=Topic,y=Total,fill=Conference))
p + geom_bar(stat="identity") + theme(strip.text=element_text(size=10), 
                                      axis.text.x=element_text(angle=90, hjust=1)) 
