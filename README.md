# arkivist
Access and manipulate dictionaries and JSON files.

## Import
```python
from arkivist.arkivist import update, read
```

## Usage
**1. Reading from JSON file**
```python
people = read("people.json")
```

**2. Updating JSON file**
```python
people = read("people.json")

# item 1
person = {}
person.update({"name": "Abc Xyz"})
person.update({"age": 12})
people.update({"abcxyz": person})

# item 2
person = {}
person.update({"name": "Lmn Opq"})
person.update({"age": 15})
people.update({"lmnopq": person})

# basic usage
update("people.json", people)

# adjust indent
update("people.json", people, indent=3)

# sort and reverse order
update("people.json", people, sort=True, reverse=True)
```
