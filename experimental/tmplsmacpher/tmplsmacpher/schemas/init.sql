-- Create the 'person' table. --
CREATE TABLE main.person(
  person_id         INTEGER NOT NULL,
  author_profile_id INTEGER,
  orcid_id          INTEGER,
  affiliation       TEXT,
  email_address     TEXT,
  name              TEXT,

  PRIMARY KEY(person_id)
);

-- Create the 'author' table. --
CREATE TABLE main.author(
  person_id  INTEGER NOT NULL,
  article_id INTEGER NOT NULL,

  PRIMARY KEY(person_id, article_id)
);

-- Create the 'paper' table. --
CREATE TABLE main.paper(
  article_id               INTEGER NOT NULL,
  title                    BLOB,
  abstract                 BLOB,
  series_id                TEXT NOT NULL,
  article_publication_date TEXT,
  url                      TEXT,
  doi_number               TEXT,

  PRIMARY KEY(series_id)
);

-- Create the 'conference' table. --
CREATE TABLE main.conference(
  series_id       TEXT NOT NULL,
  proc_id         INTEGER,
  acronym         TEXT,
  isbn13          TEXT,
  year            TEXT,
  name            TEXT,
  series_title    TEXT,
  series_vol      TEXT,

  PRIMARY KEY(series_id)
);

-- Create the 'score' table. --
CREATE TABLE main.score(
  article_id INTEGER NOT NULL,
  topic_id   INTEGER,
  model_id   INTEGER NOT NULL,
  score      REAL,

  PRIMARY KEY(article_id, topic_id, model_id)
);

-- Create the 'model' table. --
CREATE TABLE main.model(
  model_id INTEGER NOT NULL,
  path     TEXT,

  PRIMARY KEY(model_id)
);
