#!/usr/bin/env python
# coding=utf-8

from setuptools import setup
from setuptools import find_packages

setup(
    name="lbnlp",
    version="1.0",
    license='Apache License 2.0',

    packages=find_packages(),
    platforms="any",

    install_requires=[
        "hanlp@git+https://github.com/yick2232/HanLP.git",
        "tensorflow==2.4.0",
        "bert-for-tf2==0.14.7",
        "jieba",
        "gensim",
        "oss2",
    ],

    zip_safe=False
)
