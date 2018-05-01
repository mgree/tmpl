# tmplsmacpher
A python package used for running, saving, and manipulating topic models
over the ACM Digital Library corpus.

Built using Scikit-learn's topic modeling implementations.

## Components

### models
Directory where trained topic models are stored.
Each individual topic model is stored under its own directory with the following
files:
- _model.pkl_: The raw pickled TopicModel class representing this topic model.
- _db.sqlite3_: Sqlite3 database containing metadata and topic scores.
- _summary.txt_: Text file that summarizes the results of the topic model into a human (fast) readable form.

### notebooks
Directory containing jupyter notebooks used to help evaluate models. As of now,
this only contains a notebook that visualizes a topic model using the python
package PyLDAvis.

### schemas
Directory containing TmplDB sqlite3 schemas used to initialize TmplDB databases
(eg. create necessary tables). As of now, this contains the one schema we use
to set up a TmplDB database that represents one individual TopicModel run.

### db.py
Contains the TmplDB class. Used to create and interact with the Tmpl sqlite3
database. Each TmplDB instance is used to store data (eg. conference, paper,
author, person, model, and score data) from one topic model.

### topic_model.py
Contains the TopicModel class. Used to create, configure, interact with, and train
topic models. Also has functionality to persist topic models to TmplDB instances and 
load existing topic models.

### settings.py
Global settings file. Used to store global variables (eg. shared directory names like
the 'models' directory that store trained models in) that are shared across
the package.

### utils.py
Contains various methods that are used through the package (eg. stringToFile which
writes a given string to a given filename).

## Author
Created by Sean MacPherson (github: smacpher) Fall 2018 under the guidance
of Professor Greenberg, Pomona College.