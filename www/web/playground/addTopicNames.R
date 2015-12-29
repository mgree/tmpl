#TODO: read in a text file of topic names

setwd("/Users/evelynding/Documents/College/Junior/IW/tmpl/www/web/playground")
basedir = "/Users/evelynding/Documents/College/Junior/IW/tmpl/www/web/playground/"
output_dir = "topic_names_testing"

topic_names <- c("Register Allocation", "Program Transformation", "Concurrency", "Parsing", "Object-oriented", "Models and Modeling", "Language Design", "Parallelism", "Program Logics", "Applications", "Test generation", "Verification", "Type systems", "Components and APIs")
input_len = length(topic_names)

#replace ldavis.js
fl = list.files("/Users/evelynding/Documents/College/Junior/IW/tmpl/www/web/playground/htmljs", full.names = TRUE)
file.copy(fl, output_dir, overwrite = TRUE)

#write to lda.json with topic names
fr <- file(paste(basedir,output_dir, "/lda.json", sep = ""), open = "rt")
file.create(paste(output_dir, "/lda_temp.json", sep = ""))
fw <- file(paste(output_dir, "/lda_temp.json", sep = ""), open = "wt")
header <- readLines(fr, n=4)
writeLines(header, con=fw)
numTopics <- readLines(fr, n=1)
print(numTopics)
#check that number of topics matches length of input
library(stringr)
commaCount = str_count(numTopics, ',')
print(commaCount)
print (input_len)
if (commaCount != input_len) {
  stop("Number of topic names does not match number of topics", domain = NULL)
}
writeLines(numTopics, con=fw)

new_line <-paste (topic_names, collapse = '", "')
new_line <- paste ('"topic_names": ["', new_line, '"],', sep= "")
print (new_line)
writeLines(new_line, con=fw)
remaining_file <- readLines(fr, n=-1)
writeLines(remaining_file, con=fw)
close(fr)
close(fw)
file.rename(paste(basedir,output_dir, "/lda_temp.json", sep = ""), paste(basedir,output_dir, "/lda.json", sep = ""))