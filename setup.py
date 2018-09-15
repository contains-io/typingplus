#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Install typingplus."""

from __future__ import unicode_literals

from setuptools import setup


setup(
    name='typingplus',
    use_scm_version=True,
    description='An enhanced typing library with casting and validation.',
    long_description=open('README.rst').read(),
    author='Melissa Nuño',
    author_email='dangle@contains.io',
    url='https://github.com/contains-io/typingplus',
    keywords=['typing', 'schema' 'validation', 'types', 'pep484',
              'annotations', 'type comments'],
    license='MIT',
    py_modules=['typingplus'],
    install_requires=[
        'typing >= 3.5.3 ; python_version < "3.7.0"',
        'typing_extensions >= 3.6.2 ; python_version < "3.7.0"',
        'six >= 1.10.0'
    ],
    setup_requires=[
        'six >= 1.10.0',
        'packaging',
        'appdirs',
        'pytest-runner',
        'setuptools_scm',
    ],
    tests_require=['pytest >= 3.2'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
    ]
)
