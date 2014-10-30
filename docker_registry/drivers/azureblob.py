# -*- coding: utf-8 -*-
# TODO add copyright

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

        logger.info('init with path={0}'.format(path, config))
        logger.info('azure_storage_account_name={0}'.format(self._config.azure_storage_account_name))
        logger.info('azure_storage_account_key={0}'.format(self._config.azure_storage_account_key))
        logger.info('azure_storage_container={0}'.format(self._config.azure_storage_container))

        self._container = self._config.azure_storage_container
        self._blob = BlobService(account_name=self._config.azure_storage_account_name, account_key=self._config.azure_storage_account_key)

        self._init_container()

        self._root_path = path or './tmp' # TODO remove

    def _init_container(self):
        '''Initializes image container on Azure blob storage.
        '''
        created = self._blob.create_container(self._container, x_ms_blob_public_access='blob', fail_on_exist=False)
        if created:
            logger.info('Created blob container.')
        else:
            logger.info('Container already exists.')
        return created

    @lru.get
    def get_content(self, path):
        logger.info('get_content: path={0}'.format(path))

        try:
            return self._blob.get_blob(self._container, path)
        except azure.WindowsAzureMissingResourceError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    @lru.set
    def put_content(self, path, content):
        logger.info('put_content: path={0} content_size={1}'.format(path, len(content)))

        self._blob.put_blob(self._container, path, content, 'BlockBlob')
        return path

    def stream_read(self, path, bytes_range=None):
        logger.info('stream_read: path={0} bytes_range={1}'.format(path, bytes_range))
        
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
                    logger.info("Reading {0} bytes from buffer.".format(self.buffer_size))
                if not buf:
                    logger.info("Buf was empty.. exiting...")
                    break
                logger.info("Yielding...")
                yield buf
        except IOError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def stream_write(self, path, fp):
        # Size is mandatory
        logger.info('stream_write: path={0} fp={1}'.format(path, fp))
        self._blob.put_block_blob_from_file(self._container, path, fp)

    def list_directory(self, path=None):
        logger.info('list_directory: path={0}'.format(path))

        if not path.endswith('/'):
            path += '/' # path=a would list a/b.txt as well as 'abc.txt'

        blobs = list(self._blob.list_blobs(self._container, path))
        if not blobs:
            raise exceptions.FileNotFoundError('%s is not there' % path)
        
        return [b.name for  b in blobs]

    def exists(self, path):
        logger.info('exists: path={0}'.format(path))
        try:
            self._blob.get_blob_properties(self._container, path)
            return True
        except azure.WindowsAzureMissingResourceError:
            return False

    @lru.remove
    def remove(self, path):
        logger.info('remove: path={0}'.format(path))

        is_blob = self.exists(path)
        if is_blob:
            self._blob.delete_blob(self._container, path)
            logger.info("Deleted blob: {0}".format(path))
            return

            logger.info("Not a blob, seeing if dir: {0}".format(path))

        exists = False
        blobs = list(self._blob.list_blobs(self._container, path))
        if not blobs:
            raise exceptions.FileNotFoundError('%s is not there' % path)
        for b in blobs:
            self._blob.delete_blob(self._container, b.name)

    def get_size(self, path):
        logger.info('get_size: path={0}'.format(path))

        try:
            properties = self._blob.get_blob_properties(self._container, path)
            return long(properties['content-length'])
        except azure.WindowsAzureMissingResourceError:
            raise exceptions.FileNotFoundError('%s is not there' % path)
