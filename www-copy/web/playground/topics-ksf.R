# Load/install necessary packages
library(devtools)
library(LDAvis)

setwd("~/tmpl/www-copy/backend/test/")

phi <- read.table("final.beta")
theta <- read.table("final.gamma")
doc_length <- unlist(read.table("lengths.dat"), use.names = FALSE)
vocab <- as.character(unlist(read.table("vocab.dat"), use.names = FALSE))
token.frequency <- unlist(read.table("count.dat"), use.names = FALSE)

json <- createJSON(phi, theta, doc_length, vocab, token.frequency)

serVis(json, out.dir="temp", open.browser = FALSE)

