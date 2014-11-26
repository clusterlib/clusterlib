#!/usr/bin/env python

# Authors: Arnaud Joly
#
# License: BSD 3 clause

from distutils.core import setup

import clusterlib

NAME = 'clusterlib'
VERSION = clusterlib.__version__
AUTHOR = "Arnaud Joly"
AUTHOR_EMAIL = "arnaud.v.joly@gmail.com"
URL = 'http://clusterlib.github.io/clusterlib/'
DESCRIPTION = 'Tools to manage jobs on cluster'
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Education',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Scientific/Engineering',
    'Topic :: Utilities',
    'Topic :: Software Development :: Libraries',
]

if __name__ == '__main__':
    setup(name='clusterlib',
          version=clusterlib.__version__,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          license='BSD',
          classifiers=CLASSIFIERS,
          platforms='any',
          packages=['clusterlib', 'clusterlib.tests'])
