# Questions for Professor Greenberg.

How are we tokenizing the documents? By words? What punctuation, apostrophes (I guess those are interpreted as one word), and hyphenated terms (I did see something in the parse.py about replacing hyphens)?

Should I use stemming or lemmatization? Have we experimented with the performance / effects of both yet? I saw a `use_wordnet` flag in the parse.py file but wasn't sure if we ever set that to `False`. It seems like stemming and lemmatization would have a pretty significant effect on the performance of a topic model given that we want the topic model to be able to pick up on similar / related words.

Should I be using list comprehension to process lists of documents in place (is there a memory constraint)? Or can I non-destructively preprocess lists of documents? It might be useful to do the latter to cached intermediate results just for development purposes so that if we're testing a specific part of the pipeline, we don't have to preprocess the entire corpus each time.
