# -*- coding: utf-8 -*-

import re

from setuptools import setup, find_packages


def get_version():
    """parse __init__.py for version number instead of importing the file

    see http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
    """
    VERSIONFILE = 'dbschema/__init__.py'
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in %s.'
                           % (VERSIONFILE,))


LONG_DESCRIPTION = ''


setup(
    name='dbschema',
    version=get_version(),
    packages=find_packages(exclude=('tests',)),
    description='Inspect database schemas',
    author='Andi Albrecht',
    author_email='albrecht.andi@gmail.com',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    url='https://bitbucket.org/andialbrecht/python-dbschema',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        #'Programming Language :: Python :: Implementation :: Jython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Database',
        'Topic :: Software Development'
    ],
)
