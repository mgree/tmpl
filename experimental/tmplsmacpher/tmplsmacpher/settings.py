"""Global variables to be used throughout the package."""

# Directory to store logs in.
LOG_DIR = 'logs'

# Directory to store pickled models in. Models are pickled as TopicModel objects.
MODELS_DIR = 'models'

# File containing init file to create necessary tables in TmplDB instances.
TMPLDB_INIT_SCHEMA = 'schemas/init.sql'