"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json
import random
import requests
import threading
from .version import version, url
from random import randint

class Arkivist(dict):
    def __init__(self, data=None, filepath=None, indent=4, autosort=False, autosave=True, reverse=False, **legacy):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, str) and (filepath is None):
            filepath = filepath
        self.filepath = _validate_filepath(filepath)
        if self.filepath is not None:
            data = _read_json(self.filepath)
            if not len(self) and data is None:
                self.reload()
        self.indent = indent if indent in (1, 2, 3, 4) else 4
        self.autosort = isinstance(autosort, bool) and bool(autosort)
        self.autosave = False
        if self.filepath is not None:
            self.autosave = isinstance(autosave, bool) and bool(autosave)
        self.reverse = isinstance(reverse, bool) and bool(reverse)
        self.lock = threading.RLock()
        self.extensions = ["json", "arkivist"]
    
    def set(self, key, value):
        with self.lock:
            self.update({key: value})
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self

    def __setitem__(self, key, value):
        with self.lock:
            dict.__setitem__(self, key, value)
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self

    def fetch(self, url, extend=False):
        with self.lock:
            if extend:
                self.clear()
            try:
                with requests.get(url) as source:
                    self.update(source.json())
                if self.autosave:
                    _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
            except:
                pass
        return self

    def get(self, key, default=None):
        with self.lock:
            if key in self:
                if self[key] is not None:
                    return self[key]
            return default

    def __getitem__(self, key):
        with self.lock:
            if key in self:
                return dict.__getitem__(self, key)

    def random(self):
        with self.lock:
            if len(self):
                index = randint(0, len(self)-1)
                key = list(self.keys())[index]
                return dict({key: self.get(key)})
        return {}
    
    def count(self):
        with self.lock:
            return len(self)
    
    def is_empty(self):
        with self.lock:
            return not bool(self)

    def doublecheck(self, key, value):
        with self.lock:
            if key in self:
                return self[key] == value
        return False
    
    def flatten(self):
        with self.lock:
            return _flattener(dict(self))

    def invert(self):
        with self.lock:
            try:
                # hashable keys / values
                temp = dict(self)
                self.clear()
                self.update(dict(zip(temp.values(), temp.keys())))
                if self.autosave:
                    _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
            except:
                pass
        return self
    
    def load(self, data):
        with self.lock:
            self.clear()
            if isinstance(data, dict):
                self.update(data)
            elif isinstance(data, str):
                try:
                    self.update(json.loads(data))
                except:
                    pass
        return self
    
    def replace(self, data):
        with self.lock:
            self.clear()
            if isinstance(data, dict):
                self.update(data)
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self
    
    def reload(self):
        with self.lock:
            self.clear()
            self.update(_read_json(self.filepath))
        return self
    
    def reset(self):
        with self.lock:
            self.clear()
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self
    
    def show(self, sort=False, reverse=False):
        with self.lock:
            data = dict(self)
            if sort:
                data = dict(sorted(data.items(), reverse=reverse))
            return data
    
    def string(self, sort=False, reverse=False):
        with self.lock:
            data = dict(self)
            if sort:
                data = dict(sorted(data.items(), reverse=reverse))
            return json.dumps(data, indent=self.indent, ensure_ascii=False)
    
    def save(self, filepath=None):
        with self.lock:
            self.filepath = _validate_filepath(filepath)
            _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self

def _flattener(data):
    out = {}
    ## https://www.geeksforgeeks.org/flattening-json-objects-in-python/
    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + ".")
        elif type(x) in (list, set, tuple):
            for i in range(len(x)):
                flatten(x[i], name + str(i) + ".")
        else:
            out[name[:-1]] = x
    flatten(data)
    return out

def _validate_filepath(filepath):
    if isinstance(filepath, str):
        if filepath.split(".")[-1] != "json":
            filepath += ".json"
        try:
            with open(filepath, "w+") as temp:
                return filepath
        except:
            pass
    return None

def _read_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.loads(file.read())
    except:
        return {}

def _write_json(filepath, data, indent=4, autosort=False, reverse=False):
    filepath = _validate_filepath(filepath)
    indent = indent if indent in (1, 2, 3, 4) else 4
    if filepath is None:
        return
    data = dict(data)
    if isinstance(autosort, bool) and bool(autosort):
        reverse = isinstance(reverse, bool) and bool(reverse)
        data = dict(sorted(data.items(), reverse=reverse))
    with open(filepath, "w+", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=indent, ensure_ascii=False))