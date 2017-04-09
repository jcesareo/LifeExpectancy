# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()


setup(
    name='LifeExpectancy',
    version='0.1.0',
    description='Life Expectancy App that uses World Population API',
    long_description=readme,
    author='Jacopo Cesareo',
    author_email='jacopo87@gmail.com',
    url='https://github.com/jcesareo/LifeExpectancy',
    packages=find_packages(exclude=('tests'))
)

