"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json
import random
import getpass
import requests
import threading
from random import randint
from cryptography.fernet import Fernet

class Arkivist(dict):
    def __init__(self, data=None, filepath=None, indent=4, autosave=True, autosort=False, reverse=False, decrypt=False, credentials=None, **legacy):
        if isinstance(data, dict):
            self.update(data)
            if isinstance(filepath, str):
                self._filepath = filepath
        elif isinstance(data, str) and (filepath is None):
            self._filepath = data
        
        self._autosave = isinstance(autosave, bool) and bool(autosave)
        self._lock = threading.RLock()

        # encryption
        self._decrypt = decrypt
        self._encrypted = False

        if self._filepath is not None:
            self._encrypted, temp = _read_json(self._filepath)
            if not len(self) and temp is not None:
                self._reload()
        self._cypher = _load_cypher(self._encrypted, credentials)
        
        self._indent = indent
        self._reverse = reverse
        self._autosort = autosort

        # searching properties
        self._parent = None

        # querying properties
        self._query_complete = False
        self._operation = None
        self._child = None
        self._keyword = None
        self._exact = True
        self._sensitivity = False
        self._matches = None

    def encrypt(self, decrypt=False):
        self._decrypt = isinstance(decrypt, bool) and bool(decrypt)
        self._encrypted = isinstance(decrypt, bool) and not bool(decrypt)