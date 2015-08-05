library(ggplot2)
library(reshape2)

#topic_names <- read.csv("~/r/snapl/topic_names/abs_lda20_all4.txt",header=FALSE,as.is=TRUE)
#betas <- read.table("~/sigplan/lda/2015-01-06_11:06_lda20/final.beta",as.is=TRUE)

topic_names <- read.csv("~/r/snapl/topic_names/final_lda20_fulltext.txt",header=FALSE,as.is=TRUE)
betas <- read.table("~/sigplan/www/backend/fulltext/lda20/final.beta",as.is=TRUE)

bs <- data.matrix(betas)
betas <- data.frame(bs)
names(betas) <- topic_names[1:20,]

dists = matrix(nrow=ncol(betas), ncol=nrow(betas)+1)
dists[,1] <- c(1:ncol(betas))
for (r in c(1:nrow(betas))) {
  topic <- betas[r,]

  p <- sort(topic,decreasing = TRUE)
  p <- t(p)
  dists[,r+1] <- p
}
df <- data.frame(dists)
colnames(df) <- c("Word",topic_names[1:20,])
ll <- melt(df,c(1))
colnames(ll)[2:3] <- c("Topic","Log likelihood")

ggplot(ll,aes(x=Word,y=`Log likelihood`)) + facet_wrap(~ Topic) + geom_point() + theme(text=element_text(size = 28))
