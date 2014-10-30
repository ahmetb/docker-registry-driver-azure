# -*- coding: utf-8 -*-
# TODO add copyright

"""
docker_registry.drivers.azure
~~~~~~~~~~~~~~~~~~~~~~~~~~

Microsoft Azure Blob Storage driver.

"""

import logging
import os
import shutil

from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru

from azure.storage import BlobService

logger = logging.getLogger(__name__)

class Storage(driver.Base):

    supports_bytes_range = True

    def __init__(self, path=None, config=None):

    	self._config = config
        self._blob = BlobService(account_name=self._config.azure_account_name, account_key=self._config.azure_account_key)

        logger.info('init with path={0}'.format(path, config))
        logger.info('azure_account_name={0}'.format(self._config.azure_account_name))
        logger.info('azure_account_key={0}'.format(self._config.azure_account_key))
        logger.info('azure_storage_container={0}'.format(config.azure_storage_container))


        self._init_container()

        self._root_path = path or './tmp' # TODO remove

    def _init_container(self):
        '''Initializes image container on Azure blob storage.
        '''
        created = self._blob.create_container(self._config.azure_storage_container, x_ms_blob_public_access='blob', fail_on_exist=False)
        if created:
            logger.info('Created blob container.')
        else:
            logger.info('Container already exists.')
        return created

    def _init_path(self, path=None, create=False):
        path = os.path.join(self._root_path, path) if path else self._root_path
        if create is True:
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        return path

    @lru.get
    def get_content(self, path):
        logger.info('get_content: path={0}'.format(path))
        path = self._init_path(path)
        try:
            with open(path, mode='rb') as f:
                d = f.read()
        except Exception:
            raise exceptions.FileNotFoundError('%s is not there' % path)

        return d

    @lru.set
    def put_content(self, path, content):
        logger.info('put_content: path={0} content_size={1}'.format(path, len(content)))
        path = self._init_path(path, create=True)
        with open(path, mode='wb') as f:
            f.write(content)
        return path

    def stream_read(self, path, bytes_range=None):
        logger.info('stream_read: path={0} bytes_range={1}'.format(path, bytes_range))
        path = self._init_path(path)
        nb_bytes = 0
        total_size = 0
        try:
            with open(path, mode='rb') as f:
                if bytes_range:
                    f.seek(bytes_range[0])
                    total_size = bytes_range[1] - bytes_range[0] + 1
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
        # Size is mandatory
        logger.info('stream_write: path={0} fp={1}'.format(path, fp))

        path = self._init_path(path, create=True)
        with open(path, mode='wb') as f:
            try:
                while True:
                    buf = fp.read(self.buffer_size)
                    if not buf:
                        break
                    f.write(buf)
            except IOError:
                pass

    def list_directory(self, path=None):
        logger.info('list_directory: path={0}'.format(path))

        prefix = ''
        if path:
            prefix = '%s/' % path
        path = self._init_path(path)
        exists = False
        try:
            for d in os.listdir(path):
                exists = True
                yield prefix + d
        except Exception:
            pass
        if not exists:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def exists(self, path):
        logger.info('exists: path={0}'.format(path))

        path = self._init_path(path)
        return os.path.exists(path)

    @lru.remove
    def remove(self, path):
        logger.info('remove: path={0}'.format(path))

        path = self._init_path(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
            return
        try:
            os.remove(path)
        except OSError:
            raise exceptions.FileNotFoundError('%s is not there' % path)

    def get_size(self, path):
        logger.info('get_size: path=%s'.format(path))

        path = self._init_path(path)
        try:
            return os.path.getsize(path)
        except OSError:
            raise exceptions.FileNotFoundError('%s is not there' % path)
