#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='table-embeddings',
    version='0.1.0',
    author='Zian Ke, Ziheng Qin',
    author_email='kezian@umich.edu, henryqin@umich.edu',
    url='https://github.com/henryqin1997/table-embeddings',
    description='Table Embeddings project under instruction of Mike Caferalla.',
    license='MIT',
    packages=['etl'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['nltk==3.3',
                      'numpy==1.15.1',
                      'six==1.11.0'],
)