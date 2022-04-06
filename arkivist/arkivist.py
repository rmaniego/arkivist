"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json
import random
import requests
import threading
from random import randint

class Arkivist(dict):
    def __init__(self, data=None, filepath=None, indent=4, autosave=True, autosort=False, reverse=False, **legacy):
        if isinstance(data, dict):
            self.update(data)
        elif isinstance(data, str) and (filepath is None):
            filepath = data
        self.autosave = False
        self.lock = threading.RLock()
        self.filepath = _validate_filepath(filepath)
        if self.filepath is not None:
            temp = _read_json(self.filepath)
            if not len(self) and temp is not None:
                self.reload()
            self.autosave = isinstance(autosave, bool) and bool(autosave)
        self.indent = indent if indent in (1, 2, 3, 4) else 4
        self.autosort = isinstance(autosort, bool) and bool(autosort)
        self.reverse = isinstance(reverse, bool) and bool(reverse)
        self.extensions = ["json", "arkivist"]

        # searching properties
        self.parent = None

        # querying properties
        self.query_complete = False
        self.operation = None
        self.child = None
        self.keyword = None
        self.exact = True
        self.sensitivity = False
        self.matches = None
    
    def find(self, parent):
        with self.lock:
            self.parent = None
            if parent in self:
                self.parent = parent
        return self
    
    def set(self, key, value):
        with self.lock:
            if self.parent is not None:
                if self.parent in self:
                    self[self.parent][key] = value
            else:
                self[key] = value
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
            if self.parent is not None:
                if self.parent in self:
                    if isinstance((temp:=self[self.parent]), dict):
                        if key in temp:
                            return temp[key]
            else:
                if key in self:
                    if self[key] is not None:
                        return self[key]
            return default

    def __getitem__(self, key):
        with self.lock:
            if key in self:
                return dict.__getitem__(self, key)
    
    def appendIn(self, key, value, unique=False, sort=False):
        with self.lock:
            unique = isinstance(unique, bool) and bool(unique)
            sort = isinstance(sort, bool) and bool(sort)
            if self.parent is not None:
                if self.parent in self:
                    if key not in self[self.parent]:
                        self[self.parent][key] = []
                    if isinstance(self[self.parent][key], list):
                        if type(value) in (list, set, tuple):
                            self[self.parent][key].extend(value)
                        else:
                            self[self.parent][key].append(value)
                        try:
                            if sort:
                                self[self.parent][key] = list(sorted(self[self.parent][key]))
                        except:
                            pass
                        try:
                            if unique:
                                self[self.parent][key] = list(set(self[self.parent][key]))
                        except:
                            pass
            else:
                if key not in self:
                    self[key] = []
                if isinstance(self[key], list):
                    if type(value) in (list, set, tuple):
                        self[key].extend(value)
                    else:
                        self[key].append(value)                    
                    try:
                        if sort:
                            self[key] = list(sorted(self[key]))
                    except:
                        pass
                    try:
                        if unique:
                            self[key] = list(set(self[key]))
                    except:
                        pass
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self
    
    def removeIn(self, key, value       ):
        with self.lock:
            if type(value) not in (list, set, tuple):
                value = [value]
            if self.parent is not None:
                if self.parent in self:
                    if key in self[self.parent]:
                        if isinstance(self[self.parent][key], list):
                            self[self.parent][key] = list(set(self[self.parent][key]) - set(value))
            else:
                if key in self:
                    if isinstance(self[key], list):
                        self[key] = list(set(self[key]) - set(value))
            if self.autosave:
                _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self

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
    
    # quering methods
    def where(self, child, keyword=None, exact=False, sensitivity=True):
        with self.lock:
            self.operation = "matches"
            self.child = child
            self.keyword = keyword
            self.exact = exact
            self.sensitivity = sensitivity
            self.query_complete = False
            if keyword is not None:
                if self.matches is None:
                    self.matches = dict(self)
                self.matches = _query(self.matches, self.operation, self.child, self.keyword, self.exact, self.sensitivity)
                self.query_complete = True
        return self
    
    def exclude(self, keyword=None, exact=False, sensitivity=True):
        with self.lock:
            self.operation = "exclude"
            self.keyword = keyword
            self.exact = exact
            self.sensitivity = sensitivity
            if self.matches is None:
               self.matches = dict(self)
            self.matches = _query(self.matches, self.operation, self.child, self.keyword, self.exact, self.sensitivity)
            self.query_complete = True
        return self
    
    def query(self, sort=False, reverse=False):
        with self.lock:
            if self.matches is None:
                self.matches = dict(self)
            if self.operation is not None and not self.query_complete:
                self.matches = _query(self.matches, self.operation, self.child, self.keyword, self.exact, self.sensitivity)
            temp = self.matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self.query_complete = False
            self.operation = None
            self.child = None
            self.keyword = None
            self.exact = None
            self.sensitivity = None
            self.matches = None
            for key, value in temp.items():
                yield key, value
    
    def show(self, sort=False, reverse=False):
        with self.lock:
            if self.matches is None:
                self.matches = dict(self)
            if self.operation is not None and not self.query_complete:
                self.matches = _query(self.matches, self.operation, self.child, self.keyword, self.exact, self.sensitivity)
            temp = self.matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self.query_complete = False
            self.operation = None
            self.child = None
            self.keyword = None
            self.exact = None
            self.sensitivity = None
            self.matches = None
            return temp
    
    def string(self, sort=False, reverse=False):
        with self.lock:
            if self.matches is None:
                self.matches = dict(self)
            if self.operation is not None and not self.query_complete:
                self.matches = _query(self.matches, self.operation, self.child, self.keyword, self.exact, self.sensitivity)
            temp = self.matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self.query_complete = False
            self.operation = None
            self.child = None
            self.keyword = None
            self.exact = None
            self.sensitivity = None
            self.matches = None
            return temp
            return json.dumps(temp, indent=self.indent, ensure_ascii=False)
    
    def save(self, filepath=None):
        with self.lock:
            _write_json(self.filepath, self, indent=self.indent, autosort=self.autosort, reverse=self.reverse)
        return self

def _query(collection, operation, child, keyword, exact, sensitivity):
    matches = {}
    if operation not in ("matches", "exclude"):
        return collection
    sensitivity = isinstance(sensitivity, bool) and bool(sensitivity)
    def evaluate(operation, keyword, value):
        evaluation = (keyword == value)
        if not exact:
            if type(value) in (str, list, set, tuple, dict):
                evaluation = (keyword in value)
        if operation == "matches":
            return evaluation
        return not evaluation
    for parent, data in collection.items():
        value = None
        if child is not None:
            value = data.get(child, None)
        if not sensitivity and isinstance(value, str):
            keyword = keyword.lower()
            value = value.lower()
        if evaluate(operation, keyword, value):
            matches.update({parent: data})
    return matches

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
            with open(filepath, "a+") as temp:
                return filepath
        except:
            pass
    return None

def _read_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    except:
        return {}

def _write_json(filepath, data, indent=4, autosort=False, reverse=False):
    filepath = _validate_filepath(filepath)
    indent = indent if indent in (1, 2, 3, 4) else 4
    if filepath is None:
        return
    if data is None:
        return
    data = dict(data)
    if isinstance(autosort, bool) and bool(autosort):
        reverse = isinstance(reverse, bool) and bool(reverse)
        data = dict(sorted(data.items(), reverse=reverse))
    with open(filepath, "w+", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=indent, ensure_ascii=False))