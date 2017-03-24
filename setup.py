#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install typingplus."""

from __future__ import unicode_literals

from setuptools import setup
from setuptools import find_packages


setup(
    name='typingplus',
    use_scm_version=True,
    description='An enhanced typing library with casting and validation.',
    long_description=open('README.rst').read(),
    author='Dangle Nuño',
    author_email='dangle@contains.io',
    url='https://github.com/contains-io/typingplus',
    keywords=['typing', 'schema' 'validation', 'types'],
    license='MIT',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=[
        'typing >= 3.5.3',
        'six >= 1.10.0'
    ],
    setup_requires=[
        'six >= 1.10.0',
        'packaging',
        'appdirs',
        'pytest-runner',
        'setuptools_scm',
    ],
    tests_require=['pytest >= 3.0'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
    ]
)
