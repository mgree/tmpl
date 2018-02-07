# Questions for Professor Greenberg.
## Notes: date denotes weekly check-in date.

02/05/2018
How are we tokenizing the documents? By words? What punctuation, apostrophes (I guess those are interpreted as one word), and hyphenated terms (I did see something in the parse.py about replacing hyphens)?

Should I use stemming or lemmatization? Have we experimented with the performance / effects of both yet? I saw a `use_wordnet` flag in the parse.py file but wasn't sure if we ever set that to `False`. It seems like stemming and lemmatization would have a pretty significant effect on the performance of a topic model given that we want the topic model to be able to pick up on similar / related words.

Note: It might be useful to do the latter to cached intermediate results just for development purposes so that if we're testing a specific part of the pipeline, we don't have to preprocess the entire corpus each time.

How do I determine which of the xml files contain abstracts vs. full-texts? How many entries are in each .xml file?

Does the .dtd file work for both abstracts and full-texts?

02/12/2018
I remember reading something in the PL Topic Modeling paper that said that the
titles were appended to the abstracts in the abstract corpus. Do we want to do
that this time around, too? What are the benefits of doing that? Should titles be
"weighted" differently than the contents of the abstract?
