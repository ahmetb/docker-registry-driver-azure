#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014 Ahmet Alp Balkan <ahmetalpbalkan@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools


__author__ = 'Ahmet Alp Balkan'
__copyright__ = 'Copyright 2014'
__credits__ = []

__version__ = '1.1'
__maintainer__ = 'Ahmet Alp Balkan'
__email__ = 'ahmetalpbalkan@gmail.com'

__title__ = 'docker-registry-driver-azureblob'
__build__ = 0x000000

__url__ = 'https://github.com/ahmetalpbalkan/docker-registry-driver-azure'
__description__ = 'Docker registry Azure Blob Storage driver'
d = 'https://github.com/ahmetalpbalkan/docker-registry-driver-azure/archive/master.zip'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    download_url=d,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: Apache Software License'],
    platforms=['Independent'],
    namespace_packages=['docker_registry',
                        'docker_registry.drivers'],
    packages=['docker_registry',
              'docker_registry.drivers'],
    install_requires=[
        "azure>=0.8.4"
    ],
    zip_safe=True
)
