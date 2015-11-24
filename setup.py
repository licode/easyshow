#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)

import sys
import warnings
import numpy as np
import versioneer

try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

from distutils.core import setup

setup(
    name='easyshow',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brookhaven National Laboratory',
    packages=['easyshow', 'easyshow.model', 'easyshow.view'],
    entry_points={'console_scripts': ['easyshow = easyshow.gui:run']},
    #package_data={'pyxrf.view': ['*.enaml'], 'configs': ['*.json']},
    include_package_data=True,
    install_requires=['matplotlib', 'enaml', 'six', 'numpy'],
    license='BSD',
    classifiers=['Development Status :: 3 - Alpha',
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Software Development :: Libraries",
                 "Intended Audience :: Science/Research"]
)
