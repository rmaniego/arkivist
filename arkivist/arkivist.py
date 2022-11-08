"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""

import re
import json
import time
import requests
import threading
from random import randint
from cryptography.fernet import Fernet

RE_WHITESPACES = re.compile(r"[\r\n]")

class Arkivist(dict):
    """Manage and manipulate JSON objects."""

    def __init__(
        self,
        data=None,
        filepath=None,
        mode="r+",
        indent=0,
        autosave=True,
        autosort=False,
        reverse=False,
        authfile=None,
        **legacy,
    ):

        self._indent = int(indent)
        self._reverse = reverse
        self._autosort = autosort
        self._autosave = autosave
        self._cypher = None
        self._encrypt = False
        self._authfile = None
        self._lock = threading.RLock()
        
        self._read_mode = "r+"
        if mode not in ("r", "r+", "w+"):
            ArkivistException("Unsupported file read mode, use `r`, `r+`, `w+`.")
        self._read_mode = mode

        self._save_as = None
        self._filepath = None
        self._is_data = isinstance(data, dict)
        if self._is_data:
            self.update(data)
            if isinstance(filepath, str):
                self._filepath = filepath
        elif isinstance(data, str) and (filepath is None):
            self._filepath = data

        if isinstance(authfile, str):
            self._authfile = authfile
            self._cypher = _load_cypher(self._authfile)

        if not self._is_data and self._filepath:
            self._encrypt, data = _read_json(self._filepath, self._read_mode, self._cypher)
            self.update(data)
            self.save()

        # searching properties
        self._parent = None
        self._query_complete = False
        self._operation = None
        self._child = None
        self._keyword = None
        self._exact = True
        self._sensitivity = False
        self._matches = None

    def encrypt(self, state=True):
        """Set Encrypt/Decrypt configuration for JSON file"""
        with self._lock:
            if not self._encrypt and state:
                self._encrypt = True
                # create dynamic filename if custom filename is invalid
                self._authfile = _new_encryption_key(self._authfile)
                self._cypher = _load_cypher(self._authfile)
            elif (self._encrypt and self._cypher is not None) and not state:
                self._encrypt = False
                self._cypher = None
            self.save()

    def find(self, parent):
        with self._lock:
            self._parent = None
            if parent in self:
                self._parent = parent
            return self

    def set(self, key, value):
        with self._lock:
            if self._parent is not None:
                if self._parent in self:
                    self[self._parent][key] = value
                self._parent = None
            else:
                self[key] = value
            _write_json(self)
            return self

    def __setitem__(self, key, value):
        with self._lock:
            dict.__setitem__(self, key, value)
            _write_json(self)
            return self

    def fetch(self, url, extend=False, noerror=True):
        with self._lock:
            if not extend:
                self.clear()
            try:
                with requests.get(url) as source:
                    self.update(source.json())
            except Exception as e:
                if not noerror:
                    ArkivistException(str(e))
            _write_json(self)
            return self

    def get(self, key, default=None):
        with self._lock:
            if self._parent is not None:
                if self._parent in self:
                    if isinstance((temp := self[self._parent]), dict):
                        if key in temp:
                            return temp[key]
                self._parent = None
            else:
                if key in self:
                    if self[key] is not None:
                        return self[key]
            return default

    def __getitem__(self, key):
        with self._lock:
            if key in self:
                return dict.__getitem__(self, key)

    def append_in(self, key, value, unique=False, sort=False):
        with self._lock:
            unique = isinstance(unique, bool) and bool(unique)
            sort = isinstance(sort, bool) and bool(sort)
            if self._parent is not None:
                if self._parent in self:
                    if key not in self[self._parent]:
                        self[self._parent][key] = []
                    if isinstance(self[self._parent][key], list):
                        if type(value) in (list, set, tuple):
                            self[self._parent][key].extend(value)
                        else:
                            self[self._parent][key].append(value)
                        try:
                            if sort:
                                self[self._parent][key] = list(
                                    sorted(self[self._parent][key])
                                )
                        except:
                            pass
                        try:
                            if unique:
                                self[self._parent][key] = list(
                                    set(self[self._parent][key])
                                )
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
            _write_json(self)
            return self

    def remove_in(self, key, value):
        with self._lock:
            if type(value) not in (list, set, tuple):
                value = [value]
            if self._parent is not None:
                if self._parent in self:
                    if key in self[self._parent]:
                        if isinstance(self[self._parent][key], list):
                            self[self._parent][key] = list(
                                set(self[self._parent][key]) - set(value)
                            )
            else:
                if key in self:
                    if isinstance(self[key], list):
                        self[key] = list(set(self[key]) - set(value))
            _write_json(self)
            return self

    def random(self):
        with self._lock:
            if len(self):
                index = randint(0, len(self) - 1)
                key = list(self.keys())[index]
                return dict({key: self.get(key)})
            return {}

    def count(self):
        with self._lock:
            return len(self)

    def is_empty(self):
        with self._lock:
            return not bool(self)

    def doublecheck(self, key, value):
        with self._lock:
            if key in self:
                return self[key] == value
            return False

    def flatten(self):
        with self._lock:
            return _flattener(dict(self))

    def invert(self):
        with self._lock:
            temp = dict(self)
            self.clear()
            self.update(dict(zip(temp.values(), temp.keys())))
            _write_json(self)
            return self

    def load(self, data):
        with self._lock:
            self.clear()
            if isinstance(data, dict):
                self.update(data)
            elif isinstance(data, str):
                try:
                    self.update(json.loads(data))
                except:
                    pass
            _write_json(self)
            return self

    def reload(self):
        with self._lock:
            self._encrypt, temp = _read_json(self._filepath, self._read_mode, self._cypher)
            if len(temp):
                self.clear()
                self.update(temp)
            return self

    def reset(self):
        with self._lock:
            self.clear()
            _write_json(self)
            return self

    # quering methods
    def where(self, child, keyword=None, exact=False, sensitivity=True):
        with self._lock:
            self._operation = "matches"
            self._child = child
            self._keyword = keyword
            self._exact = exact
            self._sensitivity = sensitivity
            self._query_complete = False
            if keyword is not None:
                if self._matches is None:
                    self._matches = dict(self)
                self._matches = _query(
                    self._matches,
                    self._operation,
                    self._child,
                    self._keyword,
                    self._exact,
                    self._sensitivity,
                )
                self._query_complete = True
            return self

    def exclude(self, keyword=None, exact=False, sensitivity=True):
        with self._lock:
            self._operation = "exclude"
            self._keyword = keyword
            self._exact = exact
            self._sensitivity = sensitivity
            if self._matches is None:
                self._matches = dict(self)
            self._matches = _query(
                self._matches,
                self._operation,
                self._child,
                self._keyword,
                self._exact,
                self._sensitivity,
            )
            self._query_complete = True
            return self

    def query(self, sort=False, reverse=False):
        with self._lock:
            if self._matches is None:
                self._matches = dict(self)
            if self._operation is not None and not self._query_complete:
                self._matches = _query(
                    self._matches,
                    self._operation,
                    self._child,
                    self._keyword,
                    self._exact,
                    self._sensitivity,
                )
            temp = self._matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self._query_complete = False
            self._operation = None
            self._child = None
            self._keyword = None
            self._exact = None
            self._sensitivity = None
            self._matches = None
            for key, value in temp.items():
                yield key, value

    def show(self, sort=False, reverse=False):
        with self._lock:
            if self._matches is None:
                self._matches = dict(self)
            if self._operation is not None and not self._query_complete:
                self._matches = _query(
                    self._matches,
                    self._operation,
                    self._child,
                    self._keyword,
                    self._exact,
                    self._sensitivity,
                )
            temp = self._matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self._query_complete = False
            self._operation = None
            self._child = None
            self._keyword = None
            self._exact = None
            self._sensitivity = None
            self._matches = None
            return temp

    def string(self, sort=False, reverse=False):
        with self._lock:
            if self._matches is None:
                self._matches = dict(self)
            if self._operation is not None and not self._query_complete:
                self._matches = _query(
                    self._matches,
                    self._operation,
                    self._child,
                    self._keyword,
                    self._exact,
                    self._sensitivity,
                )
            temp = self._matches
            if sort:
                temp = dict(sorted(temp.items(), reverse=reverse))
            # clears query data after the operation
            self._query_complete = False
            self._operation = None
            self._child = None
            self._keyword = None
            self._exact = None
            self._sensitivity = None
            self._matches = None
            if self._indent:
                return json.dumps(temp, indent=self._indent, ensure_ascii=False)
            return json.dumps(temp, ensure_ascii=False)

    def save(self, save_as=None):
        with self._lock:
            self._save_as = save_as
            _write_json(self, forced=True)
            self._save_as = None


def _query(collection, operation, child, keyword, exact, sensitivity):
    matches = {}
    if operation not in ("matches", "exclude"):
        return collection
    sensitivity = isinstance(sensitivity, bool) and bool(sensitivity)

    def evaluate(operation, keyword, value):
        evaluation = keyword == value
        if not exact:
            if type(value) in (str, list, set, tuple, dict):
                evaluation = keyword in value
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
    """Flatten nested JSON object."""
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


def _new_encryption_key(authfile):
    if not isinstance(authfile, str):
        timestamp = str(int(time.time()))
        authfile = f"arkivist-auth-{timestamp}.txt"
    with open(authfile, "w+", encoding="utf-8") as f:
        f.write(Fernet.generate_key().decode())
    return authfile


def _load_cypher(authfile):
    if authfile is None:
        return None
    filepath = _validate_filepath(authfile, extension="txt")
    with open(filepath, "r") as f:
        return Fernet(f.read().encode("utf-8"))


def _validate_filepath(filepath, extension="json"):
    if filepath.split(".")[-1].lower() == extension:
        return filepath
    ArkivistException("Unsupported file.")


def _read_json(filepath, mode, cypher=None):
    """ Read and parse JSON file to Python dictionary. """
    temp = ""
    encrypt, content = False, {}
    filepath = _validate_filepath(filepath)
    keys = ("arkivist", "encryption", "content")
    try:
        with open(filepath, mode, encoding="utf-8") as f:
            temp = RE_WHITESPACES.sub("", f.read()).strip()
            if mode == "w+":
                f.write(temp)
    except:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("{}")
    if temp[:2] in ("", "{}"):
        return encrypt, content
    content = json.loads(temp)
    if len(content) == len(keys):
        encrypt = all([(key in content) for key in keys])
        if encrypt and cypher is not None:
            if not (
                content["arkivist"] >= 1.2 and content["encryption"] == "fernet"
            ):
                ArkivistException("The file is not compatible with Arkivist.")
            encrypted = content["content"].encode("utf-8")
            decrypted = cypher.decrypt(encrypted).decode().strip()
            decrypted = decrypted if decrypted else "{}"
            content = json.loads(decrypted)
    return encrypt, content

def _write_json(obj, forced=False):
    """Write JSON object as string representation into file."""
    if not any([forced, obj._autosave]):
        return

    if obj._save_as is not None:
        obj._filepath = obj._save_as
    filepath = _validate_filepath(obj._filepath)

    dataset = dict(obj)
    autosort = isinstance(obj._autosort, bool) and bool(obj._autosort)
    if autosort:
        reverse = isinstance(obj._reverse, bool) and bool(obj._reverse)
        dataset = dict(sorted(obj.items(), reverse=reverse))

    # string representation of the JSON object
    content = ""
    encrypt = isinstance(obj._encrypt, bool) and bool(obj._encrypt)
    if encrypt:
        encrypted = {}
        encrypted["arkivist"] = 1.3
        encrypted["encryption"] = "fernet"
        encrypted["content"] = obj._cypher.encrypt(
            content.encode("utf-8")
        ).decode()
        content = json.dumps(encrypted, ensure_ascii=False)
    else:
        indent = obj._indent if obj._indent in (0, 1, 2, 3, 4) else 4
        content = json.dumps(dataset, indent=indent, ensure_ascii=False)
    with open(filepath, "w+", encoding="utf-8") as f:
        f.write(content)


class ArkivistException(Exception):
    """Generic Arkivist exception."""

    def __init__(self, message):
        super().__init__(message)
