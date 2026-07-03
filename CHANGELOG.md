# Changelog

## 1.4.0 (2026-07-04)

Major stability, reliability, security, and developer-experience release.
The public API is fully backward compatible: no methods were removed.

### Fixed
- **Encryption data loss**: encrypted saves previously encrypted an empty
  string instead of the actual contents, so every encrypted file was saved
  empty. Encrypted files now round-trip correctly.
- **`find()` state leaks**: the parent selected by `find()` was not cleared
  after `get()`, `append_in()`, or `remove_in()`, silently redirecting the
  next unrelated operation into the parent. The marker is now always cleared,
  even when an operation raises.
- **`save(save_as=...)` redirected the file**: saving a copy permanently
  changed the backing filepath, so later autosaves went to the copy. It now
  writes a copy and keeps autosaving to the original file.
- **Failed `fetch()` wiped data**: contents were cleared *before* the HTTP
  request, so a failed request (with the default `noerror=True`) silently
  erased everything and saved the empty result. Data is now only replaced
  after a successful response.
- **`load()` with invalid input wiped data**: invalid JSON strings were
  silently ignored *after* clearing, erasing the contents. Invalid input now
  raises `ArkivistException` and leaves the data untouched.
- **`encrypt()` overwrote existing key files**: re-enabling encryption
  regenerated the authfile, making previously encrypted files unreadable.
  Existing key files are now never overwritten.
- **`mode="r"` silently created missing files**: it now raises
  `ArkivistException`, matching the documented behavior.
- `append_in(..., unique=True, sort=True)` no longer destroys the sort order
  (deduplication ran through `set()` after sorting); `remove_in()` no longer
  reorders or deduplicates the remaining items.
- Querying with `exact=False` on non-container values (e.g. integers) no
  longer raises `TypeError`; rows whose values are not dictionaries no longer
  crash `where()`.
- Reading an encrypted file without an authfile now raises a clear error
  instead of loading the raw envelope as data.

### Reliability
- **Atomic writes**: files are written to a temporary file and moved into
  place with `os.replace()`, so an interrupted write can no longer truncate
  or corrupt the JSON file.
- **Full thread safety**: every operation (including inherited `dict`
  mutations) is guarded by a re-entrant lock; `query()` no longer holds the
  lock while yielding.
- Native `dict` mutations — `update()`, `pop()`, `popitem()`, `clear()`,
  `setdefault()`, `del d[key]` — now honor autosave and the lock, consistent
  with `set()`.
- Corrupted JSON, non-object roots, and unreadable files raise descriptive
  `ArkivistException`s (with the original exception chained) instead of
  bare `json`/`OSError` tracebacks or silent file resets.
- `invert()` validates that values are hashable before clearing, so a
  failure no longer destroys the contents.
- Parent directories are created automatically when saving to a nested path.

### Security
- New encryption key files are created with restrictive permissions (0o600
  where the platform supports it) and `O_EXCL` (never clobbering a file).
- `fetch()` only accepts `http://` and `https://` URLs, applies a
  configurable `timeout` (default 10s) instead of hanging forever, and
  raises on HTTP error statuses.
- Wrong-key decryption failures raise a clear `ArkivistException` instead of
  leaking library internals.

### Performance / memory
- `import arkivist` no longer imports `requests` or `cryptography`; they are
  loaded lazily on first use, cutting import time and baseline memory.
- Saving no longer makes a full copy of the dictionary unless `autosort` is
  enabled.
- New `batch()` context manager suspends autosave for bulk operations and
  writes once at the end.
- `random()` uses `random.choice` instead of building an index list.

### Added
- `batch()` — context manager for bulk mutations with a single save.
- `matches(key, value)` — replacement for `doublecheck()`.
- `to_json(sort, reverse, indent)` — JSON string with per-call indent.
- Context-manager support: `with Arkivist("f.json", autosave=False) as a: ...`
  saves on exit.
- Read-only properties `filepath`, `authfile`, `encrypted`, and a
  `autosave` property that can also be assigned.
- `Arkivist(filepath="data.json")` now works with the keyword alone
  (previously the keyword was ignored unless `data` was a dictionary).
- Passing `authfile` for a file that does not exist yet is now allowed; the
  key is generated at that path by `encrypt()`.
- `pyproject.toml`, a full `unittest`/`pytest`-compatible test suite under
  `tests/`, and a `.gitignore`.

### Deprecated (still functional, emit `DeprecationWarning`)
- `count()` — use the built-in `len()`.
- `doublecheck()` — use `matches()`.
- Unknown legacy keyword arguments to `Arkivist(...)` now warn instead of
  being silently ignored.
