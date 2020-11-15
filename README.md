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

**3a. Arkivist class, show variations**
```python
from arkivist import Arkivist


people = Arkivist("test.json")

person = {}
person.update({"name": "Juan"})
people.set({"juan": person})

print("Show all items (unsorted):\t", people.show())
print("Show all items (sorted):\t", people.show(sort=True))
print("Show all items (reverse):\t", people.show(sort=True, reverse=True))
```


**3b. Arkivist class, manual save and search**
```python
from arkivist import Arkivist

## autosave = False
people = Arkivist("test.json", autosave=False)

person = {}
person.update({"name": "Maria"})
people.set({"maria": person})

# manual saving
people.save()

# save to another file
people.save(filepath="test.backup.json")

# search in dictionary
maria = people.search("maria", fallback="")
print("Search for Maria:\t\t", maria)
```

**4. Replace and clear dictionary**
```python
from arkivist import Arkivist

people = Arkivist("test.json", autosave=False)

# print the number of entries
print("Count:\t\t", people.count())
```

**5. Replace and clear dictionary**
```python
from arkivist import Arkivist

people = Arkivist("test.json", autosave=False)

# print original contents
print("Old:\t\t", people.show())

# print new contents
alien = {"anon": {"name": "Anon"}}
people.replace(alien)
print("New:\t\t", people.show())

# print empty dictionary
people.clear()
print("Clear:\t\t", people.show())
```