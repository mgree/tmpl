#!/usr/bin/python
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='fathom',
    description='''A package to streamline Tmpl topic modeling.''',
    author_email='sean.j.macpherson@gmail.com',
    version='0.0.1',
    author='Sean MacPherson',
    install_requires=required,
)
