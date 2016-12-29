#!/usr/bin/env python
#

import setuptools

import vetoes


version = vetoes.version
try:
    with open('LOCAL-VERSION') as version_file:
        version += version_file.readline().strip()
except IOError:
    pass


setuptools.setup(
    name='vetoes',
    version=version,
    description='Rejected companion library',
    packages=['vetoes'],
    url='https://github.com/dave-shawley/vetoes',
    author='Dave Shawley',
    author_email='daveshawley+python@gmail.com',
    long_description='\n'+open('README.rst').read(),
    install_requires=['rejected'],
    platforms='any',
    classifiers=['Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 3',
                'Development Status :: 4 - Beta'],
)
