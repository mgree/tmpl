#!/usr/bin/python
import os
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='tmplsmacpher',
    version='0.0.1',
    author='Sean MacPherson',
    install_requires=required,
)
