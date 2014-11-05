# -*- coding: utf-8 -*-
# Copyright Ahmet Alp Balkan <ahmetalpbalkan@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
docker_registry.drivers.azure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Microsoft Azure Blob Storage driver.

"""

import io
import logging
import os
import shutil

from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru

import azure
from azure.storage import BlobService

logger = logging.getLogger(__name__)


class Storage(driver.Base):

    supports_bytes_range = True

    def __init__(self, path=None, config=None):
        self._config = config
        self._container = self._config.azure_storage_container

        protocol = 'https' if self._config.azure_use_https else 'http'
        acct_name = self._config.azure_storage_account_name
        acct_key = self._config.azure_storage_account_key
        self._blob = BlobService(
            account_name=acct_name, account_key=acct_key, protocol=protocol)

        self._init_container()
        logger.debug("Initialized azureblob storage driver")

    def _init_container(self):
        '''Initializes image container on Azure blob storage if the container
        does not exist.
        '''
        created = self._blob.create_container(
            self._container, x_ms_blob_public_access='blob',
            fail_on_exist=False)
        if created:
            logger.info('Created blob container for image registry.')
        else:
            logger.debug('Registry container already exists.')
        return created

    @lru.get
    def get_content(self, path):
        try:
            return self._blob.get_blob(self._container, path)
        except azure.WindowsAzureMissingResourceError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    @lru.set
    def put_content(self, path, content):
        self._blob.put_blob(self._container, path, content, 'BlockBlob')
        return path

    def stream_read(self, path, bytes_range=None):
        try:
            f = io.BytesIO()
            self._blob.get_blob_to_file(self._container, path, f)

            if bytes_range:
                f.seek(bytes_range[0])
                total_size = bytes_range[1] - bytes_range[0] + 1
            else:
                f.seek(0)

            while True:
                buf = None
                if bytes_range:
                    # Bytes Range is enabled
                    buf_size = self.buffer_size
                    if nb_bytes + buf_size > total_size:
                        # We make sure we don't read out of the range
                        buf_size = total_size - nb_bytes
                    if buf_size > 0:
                        buf = f.read(buf_size)
                        nb_bytes += len(buf)
                    else:
                        # We're at the end of the range
                        buf = ''
                else:
                    buf = f.read(self.buffer_size)

                if not buf:
                    break

                yield buf
        except IOError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def stream_write(self, path, fp):
        self._blob.put_block_blob_from_file(self._container, path, fp)

    def list_directory(self, path=None):
        if not path.endswith('/'):
            path += '/'  # path=a would list a/b.txt as well as 'abc.txt'

        blobs = list(self._blob.list_blobs(self._container, path))
        if not blobs:
            raise exceptions.FileNotFoundError('%s is not there' % path)

        return [b.name for b in blobs]

    def exists(self, path):
        try:
            self._blob.get_blob_properties(self._container, path)
            return True
        except azure.WindowsAzureMissingResourceError:
            return False

    @lru.remove
    def remove(self, path):
        is_blob = self.exists(path)
        if is_blob:
            self._blob.delete_blob(self._container, path)
            return

        exists = False
        blobs = list(self._blob.list_blobs(self._container, path))
        if not blobs:
            raise exceptions.FileNotFoundError('%s is not there' % path)

        for b in blobs:
            self._blob.delete_blob(self._container, b.name)

    def get_size(self, path):
        try:
            properties = self._blob.get_blob_properties(self._container, path)
            return int(properties['content-length'])  # auto-converted to long
        except azure.WindowsAzureMissingResourceError:
            raise exceptions.FileNotFoundError('%s is not there' % path)
