#!/usr/bin/python
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='riptide',
    description='''\
This is the second iteration of Tmpl built on top of Scikit-learn.
Think Tmpl V2!''',
    author_email='sean.j.macpherson@gmail.com',
    version='0.0.1',
    author='Sean MacPherson',
    install_requires=required,
)
