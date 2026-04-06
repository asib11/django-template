import os
import time
import pickle
import hashlib



CACHE_DIR = os.getenv('CACHE_DIR') or 'cache'
CACHE_EXPIRES_IN = os.getenv('CACHE_EXPIRES_IN') or 60*60*24*7
IN_MEMORY_CACHE = {}


class CacheMiss(Exception): pass


class CachedData:
    def __init__(
            self,
            key: str,
            loader=None,
            expires_in=CACHE_EXPIRES_IN,
            cache_dir=CACHE_DIR,
            cache_in_memory=False,
            cache_ignore=False,
        ):
        self.key = key.encode()
        self.expires_in = expires_in
        self._cache_dir = cache_dir
        self._loader = loader
        self._md5_path = None
        self._cache_in_memory = cache_in_memory
        self._cache_ignore = cache_ignore

    @property
    def md5_path(self):
        if self._md5_path is None:
            md5 = hashlib.md5(self.key).hexdigest()
            self._md5_path = os.path.join(
                self._cache_dir,
                md5 + '.pickle'
            )
        return self._md5_path

    def _read_file(self):
        if self._cache_ignore:
            raise CacheMiss()
        file_path = self.md5_path
        if self._cache_in_memory:
            if file_path not in IN_MEMORY_CACHE:
                raise CacheMiss()
            return IN_MEMORY_CACHE.get(file_path)

        if not os.path.exists(file_path):
            raise CacheMiss()
        with open(file_path, 'rb') as _file:
            data_container = pickle.load(_file) or {}
            return data_container

    def _write_file(self, data):
        file_path = self.md5_path
        if self._cache_in_memory:
            IN_MEMORY_CACHE[file_path] = data
        else:
            os.makedirs(self._cache_dir, exist_ok=True)
            with open(file_path, 'wb') as _file:
                pickle.dump(data, _file)

    def get_cached_data(self):
        data_container = self._read_file()
        data = data_container.get('data')
        if self.expires_in is None:
            return data
        if ('data' not in data_container) or ('expiry' not in data_container):
            raise CacheMiss()
        expiry = data_container.get('expiry')
        if expiry is None:
            return data
        if expiry > time.time():
            return data
        raise CacheMiss()

    def set_cache(self, data):
        expiry = None
        if self.expires_in is not None:
            expiry = time.time() + self.expires_in
        self._write_file({
            'key': self.key,
            'data': data,
            'expiry': expiry
        })

    def _get_data_from_loader(self):
        data = None
        loader = self._loader
        if callable(loader):
            data = loader()
        return data

    def get(self):
        try:
            return self.get_cached_data()
        except CacheMiss:
            data = self._get_data_from_loader()
            self.set_cache(data=data)
            return data





