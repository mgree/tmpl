library("ggplot2")

euclidean <- function(v1,v2) sqrt(sum(v1^2 - v2^2))

approx <- function(actual, learned) {
  err <- numeric(length=nrow(actual))
  for (i in 1:nrow(actual)) {
      err[i] <- euclidean(actual[i,],learned[i,])
  }
  return(err)
}

errByConf <- function(m, conf) {
  d <- m[which(m$Conference==conf),]
  d <- d[order(d$Year),]
  d$Conference <- NULL

  return(approx(d,d))
}

evalByYear <- function(file) {
  d <- data.frame(read.table(file,header=TRUE,sep=",",quote="\""))

  m <- aggregate(d, by=list(d$Year,d$Conference), FUN=mean)

  popl_errs <- errByConf(m, "POPL")
#  pldi_errs = errByConf(m, "PLDI")

#  return(c(popl_errs, pldi_errs))
}

evalByYear("fulltext_lda20.csv")
