"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist

    A lightweight, thread-safe Python dictionary wrapper for JSON files.
"""

import os
import json
import time
import tempfile
import threading
import warnings
from random import choice
from contextlib import contextmanager

__all__ = ["Arkivist", "ArkivistException"]

_ENVELOPE_KEYS = ("arkivist", "encryption", "content")
_ENVELOPE_VERSION = 1.3
_MIN_ENVELOPE_VERSION = 1.2


class ArkivistException(Exception):
    """Generic Arkivist exception."""

    def __init__(self, message):
        super().__init__(message)


class Arkivist(dict):
    """Manage and manipulate JSON objects backed by a JSON file.

    Behaves like a native ``dict`` with optional file persistence,
    autosave, sorting, shallow querying, and Fernet encryption.

    All mutating operations are guarded by a re-entrant lock, making a
    single instance safe to share across threads. File writes are atomic
    (written to a temporary file and moved into place), so a crash
    mid-write can no longer corrupt the JSON file.
    """

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
        self._lock = threading.RLock()

        try:
            self._indent = int(indent)
        except (TypeError, ValueError):
            raise ArkivistException("`indent` must be an integer between 0 and 4.")
        self._reverse = bool(reverse)
        self._autosort = bool(autosort)
        self._autosave = bool(autosave)
        self._cypher = None
        self._encrypt = False
        self._authfile = None

        if mode not in ("r", "r+", "w+"):
            raise ArkivistException("Unsupported file read mode, use `r`, `r+`, `w+`.")
        self._read_mode = mode

        self._save_as = None
        self._filepath = None

        # searching properties
        self._parent = None
        self._query_complete = False
        self._operation = None
        self._child = None
        self._keyword = None
        self._exact = True
        self._sensitivity = False
        self._matches = None

        if legacy:
            warnings.warn(
                "Ignoring unsupported keyword arguments: "
                + ", ".join(sorted(legacy)),
                DeprecationWarning,
                stacklevel=2,
            )

        self._is_data = isinstance(data, dict)
        if self._is_data:
            if isinstance(filepath, str):
                self._filepath = filepath
        elif isinstance(data, str) and (filepath is None):
            self._filepath = data
        elif isinstance(filepath, str):
            self._filepath = filepath

        if isinstance(authfile, str):
            self._authfile = authfile
            if os.path.exists(authfile):
                self._cypher = _load_cypher(self._authfile)

        if self._is_data:
            dict.update(self, data)
            _write_json(self)
        elif self._filepath:
            self._encrypt, loaded = _read_json(
                self._filepath, self._read_mode, self._cypher
            )
            dict.update(self, loaded)
            if self._read_mode != "r":
                _write_json(self, forced=True)

    # file and configuration properties
    @property
    def filepath(self):
        """The JSON file backing this instance, or None if in-memory only."""
        return self._filepath

    @property
    def authfile(self):
        """The path of the encryption key file, or None."""
        return self._authfile

    @property
    def encrypted(self):
        """Whether the backing file is saved encrypted."""
        return self._encrypt

    @property
    def autosave(self):
        """Whether mutations are automatically written to the backing file."""
        return self._autosave

    @autosave.setter
    def autosave(self, state):
        with self._lock:
            self._autosave = bool(state)

    def encrypt(self, state=True):
        """Set Encrypt/Decrypt configuration for JSON file.

        Enabling encryption reuses the configured authfile when it already
        exists; a new key file is only generated when none is available.
        Disabling encryption keeps the loaded key so it can be re-enabled.
        """
        with self._lock:
            if state and not self._encrypt:
                if self._cypher is None:
                    # create dynamic filename if custom filename is unset
                    self._authfile = _new_encryption_key(self._authfile)
                    self._cypher = _load_cypher(self._authfile)
                self._encrypt = True
            elif not state and self._encrypt:
                self._encrypt = False
            self.save()
            return self

    def find(self, parent):
        """Select a top-level key as the active parent for the next
        `set()`, `get()`, `append_in()`, or `remove_in()` call."""
        with self._lock:
            self._parent = parent if parent in self else None
            return self

    def set(self, key, value):
        """Insert or update a key-value pair, honoring a prior `find()`."""
        with self._lock:
            try:
                if self._parent is not None:
                    if self._parent in self:
                        container = dict.__getitem__(self, self._parent)
                        if not isinstance(container, dict):
                            raise ArkivistException(
                                f"Cannot set `{key}`: parent `{self._parent}` is not a dictionary."
                            )
                        container[key] = value
                else:
                    dict.__setitem__(self, key, value)
                _write_json(self)
            finally:
                self._parent = None
            return self

    def __setitem__(self, key, value):
        with self._lock:
            dict.__setitem__(self, key, value)
            _write_json(self)

    def __delitem__(self, key):
        with self._lock:
            dict.__delitem__(self, key)
            _write_json(self)

    def update(self, *args, **kwargs):
        """dict.update() that also persists when autosave is enabled."""
        with self._lock:
            dict.update(self, *args, **kwargs)
            _write_json(self)
            return self

    def setdefault(self, key, default=None):
        with self._lock:
            if key in self:
                return dict.__getitem__(self, key)
            dict.__setitem__(self, key, default)
            _write_json(self)
            return default

    def pop(self, key, *default):
        with self._lock:
            value = dict.pop(self, key, *default)
            _write_json(self)
            return value

    def popitem(self):
        with self._lock:
            item = dict.popitem(self)
            _write_json(self)
            return item

    def clear(self):
        with self._lock:
            dict.clear(self)
            _write_json(self)
            return self

    def fetch(self, url, extend=False, noerror=True, timeout=10, headers=None):
        """Load a JSON object from a web API.

        The existing data is only cleared after a successful response, so a
        failed request no longer wipes the current contents.
        """
        with self._lock:
            try:
                requests = _requests()
                if not isinstance(url, str) or not url.lower().startswith(
                    ("http://", "https://")
                ):
                    raise ArkivistException(
                        "Unsupported URL, only `http://` and `https://` schemes are allowed."
                    )
                with requests.get(url, timeout=timeout, headers=headers) as source:
                    source.raise_for_status()
                    payload = source.json()
                if not isinstance(payload, dict):
                    raise ArkivistException("The URL did not return a JSON object.")
                if not extend:
                    dict.clear(self)
                dict.update(self, payload)
                _write_json(self)
            except ArkivistException:
                if not noerror:
                    raise
            except Exception as e:
                if not noerror:
                    raise ArkivistException(str(e)) from e
            return self

    def get(self, key, default=None):
        with self._lock:
            try:
                if self._parent is not None:
                    if self._parent in self:
                        temp = dict.__getitem__(self, self._parent)
                        if isinstance(temp, dict) and key in temp:
                            return temp[key]
                    return default
                if key in self:
                    value = dict.__getitem__(self, key)
                    if value is not None:
                        return value
                return default
            finally:
                self._parent = None

    def __getitem__(self, key):
        with self._lock:
            if key in self:
                return dict.__getitem__(self, key)

    def append_in(self, key, value, unique=False, sort=False):
        """Append (or extend with) `value` into the list at `key`."""
        with self._lock:
            target = self._target()
            if target is None:
                return self
            if key not in target:
                dict.__setitem__(target, key, [])
            items = dict.__getitem__(target, key)
            if isinstance(items, list):
                if isinstance(value, (list, set, tuple)):
                    items.extend(value)
                else:
                    items.append(value)
                if unique:
                    try:
                        items = list(dict.fromkeys(items))
                    except TypeError:
                        pass
                if sort:
                    try:
                        items = sorted(items)
                    except TypeError:
                        pass
                dict.__setitem__(target, key, items)
            _write_json(self)
            return self

    def remove_in(self, key, value):
        """Remove one or more values from the list at `key`, preserving
        the order of the remaining items."""
        with self._lock:
            target = self._target()
            if target is not None and key in target:
                items = dict.__getitem__(target, key)
                if isinstance(items, list):
                    if not isinstance(value, (list, set, tuple)):
                        value = [value]
                    try:
                        removals = set(value)
                        items = [item for item in items if item not in removals]
                    except TypeError:
                        removals = list(value)
                        items = [item for item in items if item not in removals]
                    dict.__setitem__(target, key, items)
            _write_json(self)
            return self

    def random(self):
        """Return a random key-value pair as a dictionary."""
        with self._lock:
            if not self:
                return {}
            key = choice(tuple(dict.keys(self)))
            return {key: dict.__getitem__(self, key)}

    def count(self):
        """Deprecated: use the built-in `len()` instead."""
        _warn_deprecated("Arkivist.count()", "len(arkivist)")
        with self._lock:
            return len(self)

    def is_empty(self):
        with self._lock:
            return not bool(self)

    def doublecheck(self, key, value):
        """Deprecated: use `Arkivist.matches()` instead."""
        _warn_deprecated("Arkivist.doublecheck()", "Arkivist.matches()")
        return self.matches(key, value)

    def matches(self, key, value):
        """Check if the stored value at `key` equals `value`."""
        with self._lock:
            if key in self:
                return dict.__getitem__(self, key) == value
            return False

    def flatten(self):
        """Flatten the nested dictionary into dot-notated keys."""
        with self._lock:
            return _flattener(dict(self))

    def invert(self):
        """Swap keys and values; values must be hashable."""
        with self._lock:
            temp = dict(self)
            try:
                inverted = dict(zip(temp.values(), temp.keys()))
            except TypeError as e:
                raise ArkivistException(
                    "Cannot invert: all values must be hashable to become keys."
                ) from e
            dict.clear(self)
            dict.update(self, inverted)
            _write_json(self)
            return self

    def load(self, data):
        """Replace all contents from a dictionary or a JSON object string.

        Invalid input raises an `ArkivistException` and leaves the current
        contents untouched.
        """
        with self._lock:
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    raise ArkivistException(
                        f"Cannot load: invalid JSON string ({e})."
                    ) from e
            if not isinstance(data, dict):
                raise ArkivistException(
                    "Cannot load: expected a dictionary or a JSON object string."
                )
            dict.clear(self)
            dict.update(self, data)
            _write_json(self)
            return self

    def reload(self):
        """Re-read the backing file, replacing in-memory contents."""
        with self._lock:
            if self._filepath is None:
                return self
            self._encrypt, temp = _read_json(self._filepath, "r+", self._cypher)
            dict.clear(self)
            dict.update(self, temp)
            return self

    def reset(self):
        """Clear all contents and persist the empty object."""
        with self._lock:
            dict.clear(self)
            _write_json(self)
            return self

    @contextmanager
    def batch(self):
        """Suspend autosave for a block of operations, saving once at exit.

        Usage::

            with storage.batch():
                for i in range(10000):
                    storage.set(i, i * i)
        """
        with self._lock:
            previous = self._autosave
            self._autosave = False
        try:
            yield self
        finally:
            with self._lock:
                self._autosave = previous
                _write_json(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()
        return False

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
        """Yield the query results; the lock is released before yielding."""
        with self._lock:
            temp = self._resolve_query(sort, reverse)
        yield from temp.items()

    def show(self, sort=False, reverse=False):
        """Return the query results (or all contents) as a dictionary."""
        with self._lock:
            return self._resolve_query(sort, reverse)

    def string(self, sort=False, reverse=False):
        """Return the query results (or all contents) as a JSON string."""
        with self._lock:
            temp = self._resolve_query(sort, reverse)
            if self._indent:
                return json.dumps(temp, indent=self._indent, ensure_ascii=False)
            return json.dumps(temp, ensure_ascii=False)

    def to_json(self, sort=False, reverse=False, indent=None):
        """Return the query results (or all contents) as a JSON string,
        with an optional per-call indent override."""
        with self._lock:
            temp = self._resolve_query(sort, reverse)
            indent = self._indent if indent is None else int(indent)
            if indent:
                return json.dumps(temp, indent=indent, ensure_ascii=False)
            return json.dumps(temp, ensure_ascii=False)

    def save(self, save_as=None):
        """Write contents to the backing file, or to `save_as` as a copy.

        Saving with `save_as` writes a copy without redirecting subsequent
        autosaves away from the original filepath.
        """
        with self._lock:
            if save_as is not None:
                _validate_filepath(save_as)
            self._save_as = save_as
            try:
                _write_json(self, forced=True)
            finally:
                self._save_as = None
            return self

    # internal helpers
    def _target(self):
        """Resolve the container selected by a prior `find()`, always
        clearing the parent marker afterwards."""
        if self._parent is None:
            return self
        parent, self._parent = self._parent, None
        if parent in self:
            container = dict.__getitem__(self, parent)
            if isinstance(container, dict):
                return container
            raise ArkivistException(f"Parent `{parent}` is not a dictionary.")
        return None

    def _resolve_query(self, sort, reverse):
        """Finalize any pending query and reset the query state."""
        matches = self._matches
        if matches is None:
            matches = dict(self)
        if self._operation is not None and not self._query_complete:
            matches = _query(
                matches,
                self._operation,
                self._child,
                self._keyword,
                self._exact,
                self._sensitivity,
            )
        if sort:
            matches = dict(sorted(matches.items(), reverse=reverse))
        # clears query data after the operation
        self._query_complete = False
        self._operation = None
        self._child = None
        self._keyword = None
        self._exact = None
        self._sensitivity = None
        self._matches = None
        return matches


def _warn_deprecated(feature, replacement):
    warnings.warn(
        f"`{feature}` is deprecated and will be removed in a future release; "
        f"use `{replacement}` instead.",
        DeprecationWarning,
        stacklevel=3,
    )


def _requests():
    """Lazily import `requests` so the package works without it installed."""
    try:
        import requests
    except ImportError as e:
        raise ArkivistException(
            "The `requests` package is required for `fetch()`. "
            "Install it with `pip install requests`."
        ) from e
    return requests


def _fernet():
    """Lazily import Fernet so the package works without `cryptography`."""
    try:
        from cryptography.fernet import Fernet
    except ImportError as e:
        raise ArkivistException(
            "The `cryptography` package is required for encryption. "
            "Install it with `pip install cryptography`."
        ) from e
    return Fernet


def _query(collection, operation, child, keyword, exact, sensitivity):
    matches = {}
    if operation not in ("matches", "exclude"):
        return collection
    sensitivity = isinstance(sensitivity, bool) and bool(sensitivity)

    def evaluate(keyword, value):
        if not exact and isinstance(value, (str, list, set, tuple, dict)):
            try:
                evaluation = keyword in value
            except TypeError:
                evaluation = False
        else:
            evaluation = keyword == value
        if operation == "matches":
            return evaluation
        return not evaluation

    for parent, data in collection.items():
        value = data
        if child is not None:
            value = data.get(child, None) if isinstance(data, dict) else None
        term = keyword
        if not sensitivity and isinstance(value, str) and isinstance(term, str):
            term = term.lower()
            value = value.lower()
        if evaluate(term, value):
            matches[parent] = data
    return matches


def _flattener(data):
    """Flatten nested JSON object."""
    out = {}
    ## https://www.geeksforgeeks.org/flattening-json-objects-in-python/
    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + str(a) + ".")
        elif isinstance(x, (list, set, tuple)):
            for i, item in enumerate(x):
                flatten(item, name + str(i) + ".")
        else:
            out[name[:-1]] = x

    flatten(data)
    return out


def _new_encryption_key(authfile):
    """Create a new key file, never overwriting an existing one."""
    if not isinstance(authfile, str):
        timestamp = str(int(time.time()))
        authfile = f"arkivist-auth-{timestamp}.txt"
    if os.path.exists(authfile):
        return authfile
    Fernet = _fernet()
    key = Fernet.generate_key().decode("utf-8")
    directory = os.path.dirname(os.path.abspath(authfile))
    os.makedirs(directory, exist_ok=True)
    # restrict permissions where the platform supports it
    fd = os.open(authfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(key)
    return authfile


def _load_cypher(authfile):
    if authfile is None:
        return None
    filepath = _validate_filepath(authfile, extension="txt")
    Fernet = _fernet()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            key = f.read().strip()
        return Fernet(key.encode("utf-8"))
    except FileNotFoundError as e:
        raise ArkivistException(f"Authfile not found: `{filepath}`") from e
    except (OSError, ValueError) as e:
        raise ArkivistException(
            f"Unable to load the encryption key from `{filepath}`: {e}"
        ) from e


def _validate_filepath(filepath, extension="json"):
    if filepath is None:
        return None
    if not isinstance(filepath, str) or not filepath.strip():
        return None
    if filepath.rsplit(".", 1)[-1].lower() == extension:
        return filepath
    raise ArkivistException(
        f"Unsupported file `{filepath}`, expected a `.{extension}` file."
    )


def _read_json(filepath, mode, cypher=None):
    """Read and parse a JSON file into a Python dictionary."""
    encrypt, content = False, {}
    filepath = _validate_filepath(filepath)
    if not isinstance(filepath, str):
        return encrypt, content
    if mode == "w+":
        # start fresh; contents are written on the first save
        return encrypt, content

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            temp = f.read().strip()
    except FileNotFoundError as e:
        if mode == "r":
            raise ArkivistException(f"File not found: `{filepath}`") from e
        return encrypt, content
    except OSError as e:
        raise ArkivistException(f"Unable to read `{filepath}`: {e}") from e

    if temp in ("", "{}"):
        return encrypt, content
    try:
        content = json.loads(temp)
    except json.JSONDecodeError as e:
        raise ArkivistException(
            f"`{filepath}` does not contain valid JSON ({e})."
        ) from e
    if not isinstance(content, dict):
        raise ArkivistException(
            f"`{filepath}` must contain a JSON object at the root."
        )

    if (
        len(content) == len(_ENVELOPE_KEYS)
        and all(key in content for key in _ENVELOPE_KEYS)
        and content.get("encryption") == "fernet"
        and isinstance(content.get("content"), str)
    ):
        encrypt = True
        try:
            version = float(content["arkivist"])
        except (TypeError, ValueError):
            version = 0.0
        if version < _MIN_ENVELOPE_VERSION:
            raise ArkivistException("The file is not compatible with Arkivist.")
        if cypher is None:
            raise ArkivistException(
                f"`{filepath}` is encrypted; a valid `authfile` is required to read it."
            )
        try:
            encrypted = content["content"].encode("utf-8")
            decrypted = cypher.decrypt(encrypted).decode("utf-8").strip()
            content = json.loads(decrypted if decrypted else "{}")
        except Exception as e:
            raise ArkivistException(
                f"Failed to decrypt `{filepath}`; the authfile may not match this file."
            ) from e
    return encrypt, content


def _write_json(obj, forced=False):
    """Write JSON object as string representation into file, atomically."""
    if not (forced or obj._autosave):
        return

    filepath = obj._save_as if obj._save_as is not None else obj._filepath
    filepath = _validate_filepath(filepath)
    if not isinstance(filepath, str):
        return

    dataset = obj
    if obj._autosort:
        dataset = dict(sorted(obj.items(), reverse=bool(obj._reverse)))

    if obj._encrypt:
        if obj._cypher is None:
            raise ArkivistException(
                "Encryption is enabled but no valid authfile is loaded."
            )
        payload = json.dumps(dataset, ensure_ascii=False)
        envelope = {
            "arkivist": _ENVELOPE_VERSION,
            "encryption": "fernet",
            "content": obj._cypher.encrypt(payload.encode("utf-8")).decode("utf-8"),
        }
        content = json.dumps(envelope, ensure_ascii=False)
    else:
        indent = obj._indent if obj._indent in (0, 1, 2, 3, 4) else 4
        content = json.dumps(dataset, indent=indent, ensure_ascii=False)
    _atomic_write(filepath, content)


def _atomic_write(filepath, content):
    """Write to a temporary file and move it into place, so an interrupted
    write can never leave a truncated or corrupted JSON file behind."""
    directory = os.path.dirname(os.path.abspath(filepath))
    try:
        os.makedirs(directory, exist_ok=True)
        fd, temppath = tempfile.mkstemp(
            dir=directory, prefix=".arkivist-", suffix=".tmp"
        )
    except OSError as e:
        raise ArkivistException(f"Unable to write to `{filepath}`: {e}") from e
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(temppath, filepath)
    except OSError as e:
        try:
            os.remove(temppath)
        except OSError:
            pass
        raise ArkivistException(f"Unable to write to `{filepath}`: {e}") from e
