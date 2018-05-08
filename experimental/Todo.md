# Todo

2/05/2018
- Write class for reading xml files using the dtd files.
- Run gensim lda implementation over ACM corpus.
- Implement LDA class with caching (checkpointing at different steps in
the model construction pipeline) and easy-to-use functionality.
- Investigate gensim.corpora.bleicorpus.BleiCorpus
- Investigate gensim.models.ldamulticore (parallelized Latent Dirichlet Allocation)
- Investigate TextRank Summarizer Algorithm
- Investigate different ways to verify / parse XML (eg. untangle, xmltodict, built-in xml module)
- Investigate how to clean figures / numbers in full-text papers.

2/12/2018
- Figure out what to do with entries that are missing abstracts in the abs
corpus in tmpl-data.
- Figure out how to map and where to store metadata on files before processing
raw abstracts or fulltexts with LDA.
- Get the XML parser working for the ACM data.
- Research what 'perplexity', 'per-word bound', 'rho', 'topic diff' mean in the context of NLP and Topic Modeling.
- Fix logging formatter.
- Create a streaming corpus object for abstracts and a corpus object for full-texts: https://radimrehurek.com/gensim/tut1.html
- Might be a good idea to combine loadAllAbs and loadAllFull into one method with an arg to choose which rawtext field to choose for main document body of corpus.
- Figure out best way to load full text files.
- Investigate sklearn's LDA model.

2/26/2018
- Print out top 10 documents for each topic. Done
- Try out fulltexts corpora.
- Lower beta (make words appear in fewer topics). Trying out 'auto' eta.
- Try out BleiCorpus.

3/05/2018
- TFIDF for LDA
- Run full-text
- Parse the DL: some conferences missing: ICFP 2008 (every conference has one or two fewer than tmpl-data)

4/12/2018
- There are people with the same name but different person_id's. Maybe 'person_id' isn't a great unique identifying.
    eg. Michael Greenberg|P2338189
        Michael Greenberg|P1728711
        Michael Greenberg|P1911117

    Michael Greenberg|1863572|Matching lenses: alignment and view update
    Michael Greenberg|1640091|Flapjax: a programming language for Ajax applications
    Michael Greenberg|1706341|Contracts made manifest

TODO:
- fix dependencies (pyLDAdavis)
- make author_profile_id primary key in person table.
- brew install sqlite3 --with-functions

