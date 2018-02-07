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
- Figure out to introduce intermediate caching (eg. store mapped bag of words
on disk for later test runs); this will help speed up the development process.
- Get the XML parser working for the ACM data.
- Research what 'perplexity', 'per-word bound', 'rho', 'topic diff' mean in the context of NLP and Topic Modeling.
- Fix logging formatter.

