Topic modeling for the programming languages literature.

You can [run our tool](http://tmpl.weaselhat.com)!

# TODO

## Fix build

We're part of the way through a reorganization of the scripts in
lda. I need to reorganize how all of the input/output works, to work
with a better directory structure.

In general, (sensitive, copyrighted!) inputs are now held in a
separate repository, while the outputs will do in the `out` directory.

Currently, `lda/run_lda.sh` and some of the Python scripts are broken.
