require(ggplot2)

lda20 <- data.frame(read.table("rankings_lda20.csv",header=TRUE,sep=",",quote="\""))
lda20$Topic <- as.factor(lda20$Topic)
topic_names <- read.csv("final_lda20_fulltext.txt",header=FALSE,as.is=TRUE)

levels(lda20$Topic) <- topic_names$V1

lda50 <- data.frame(read.table("rankings_lda50.csv",header=TRUE,sep=",",quote="\""))

p50 <- ggplot(lda50,aes(x=Fulltext.Rank,y=Abstract.Rank))
p20 <- ggplot(lda20,aes(x=Fulltext.Rank,y=Abstract.Rank))

axis_labs <- labs(x = "Fulltext paper rank (out of top 50)", y = "Abstract paper rank (out of top 50)")

legend <- function (n) { guides(col=guide_legend(ncol=n)) }

# aggregate scatter plots
scatter_by_topic <- geom_point(aes(colour=factor(Topic)))
p20 + axis_labs + scatter_by_topic + legend(2) + labs(title = "Common papers in the top 50 (k=20)", colour="Topic")
p50 + axis_labs + scatter_by_topic + legend(5) + labs(title = "Common papers in the top 50 (k=50)", colour="Topic")

# by topic
p20 + geom_point() + facet_wrap(~Topic,ncol=5) + axis_labs + theme(strip.text=element_text(size=8)) # MMG this one
p50 + geom_point() + facet_wrap(~Topic,ncol=10,nrow=5) + axis_labs + labs(title="Common papers in the top 50 (k=20), by topic")

y2x <- stat_function(fun = function (x) 2 * x, colour='red')

ggplot(lda20, aes(x=Fulltext.Rank,y=Fulltext.Rank + Abstract.Rank)) + 
  geom_point(aes(colour=factor(Topic))) + 
  y2x + stat_smooth(method=lm) + 
  legend(2) + 
  labs(title="Relative rankings (k=20)\n Blue line is best linear fit w/confidence .95; red line is y = 2x (same rankings)", x="Fulltext paper rank (out of 50)", y="Fulltext rank + abstract rank (out of 50)", colour="Topic")
