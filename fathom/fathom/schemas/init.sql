-- Create the 'person' table. --
CREATE TABLE person (
  person_id         TEXT NOT NULL,
  author_profile_id INTEGER,
  orcid_id          INTEGER,
  affiliation       TEXT,
  email_address     TEXT,
  name              TEXT,

  PRIMARY KEY (person_id),
  FOREIGN KEY (person_id) REFERENCES author (person_id)
);

-- Create the 'author' table. --
CREATE TABLE author (
  person_id  TEXT NOT NULL,
  article_id INTEGER NOT NULL,

  PRIMARY KEY (person_id, article_id),
  FOREIGN KEY (article_id) REFERENCES paper (article_id)
);

-- Create the 'paper' table. --
CREATE TABLE paper (
  article_id               INTEGER NOT NULL,
  title                    BLOB,
  abstract                 BLOB,
  proc_id                  INTEGER NOT NULL,
  article_publication_date TEXT,
  url                      TEXT,
  doi_number               TEXT,

  PRIMARY KEY (article_id),
  FOREIGN KEY (proc_id) REFERENCES conference (proc_id),
  FOREIGN KEY (article_id) REFERENCES score (article_id)
);

-- Create the 'conference' table. --
CREATE TABLE conference (
  proc_id         INTEGER NOT NULL,
  series_id       TEXT,
  acronym         TEXT,
  isbn13          TEXT,
  year            TEXT,
  proc_title      TEXT,
  series_title    TEXT,
  series_vol      TEXT,

  PRIMARY KEY (proc_id)
);

-- Create the 'score' table. --
CREATE TABLE score (
  article_id INTEGER NOT NULL,
  topic_id   INTEGER,
  model_id   INTEGER NOT NULL,
  score      REAL,

  PRIMARY KEY (article_id, topic_id, model_id),
  FOREIGN KEY (model_id) REFERENCES model (model_id)
);

-- Create the 'model' table. --
CREATE TABLE model (
  model_id     TEXT NOT NULL,
  model_path   TEXT,
  timestamp     TEXT,
  num_topics   INTEGER,
  num_features INTEGER,
  max_iter     INTEGER,
  vectorizer   TEXT,
  model_type   TEXT,

  PRIMARY KEY (model_id)
);
