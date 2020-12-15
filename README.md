# arkivist
Arkivist is a lightweight python package that simplifies the management of JSON data and files. It leverages the power of Python dictionaries and JSON files, by creating a persistent storage with less complexity.

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
people.update({"juan": person})

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
people.update({"maria": person})

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

**5. Get the keys and the values**
```python
from arkivist import Arkivist

people = Arkivist("test.json", autosave=False)

# get the keys and values
print("Keys:\t\t", people.keys())
print("Values:\t\t", people.values())
```

**6. Invert the dictionary**
```python
from arkivist import Arkivist

simple = Arkivist("test.simple.json")

simple.clear()
simple.update({0: "a"})
simple.update({1: "b"})
simple.update({2: "c"})

print("Normal:\t", simple.show())
# inverts the dictionary
# keys and values must be hashable
simple.invert()
print("Invert:\t", simple.show())
```

**7. Replace and clear dictionary**
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

**8. Load new dictionary or JSON String**
```python
## Example #8
print("\nTest #8")
from arkivist import Arkivist

people = Arkivist("test.json")

# valid dictionary
people.load({"ufo": {"name": "UFO"}})
print("Valid Input: ", people.show())

# valid string
people.load('{"dog": {"name": "Doggy"}}')
print("Valid Input: ", people.show())

# flush invalid input
people.load(1234)
print("Invalid Input: ", people.show())
```

**9. Flatten any nested dictionary**
```python
## Example #9
print("\nTest #9")
from arkivist import Arkivist


people = Arkivist("test.json")

# flattens nested dictionary
people.update({"dog": {"name": "Doggy"}})
people.update({"ufo": {"name": "UFO"}})
print("Flatten: ", people.flatten().show())
```

**10. Fetch from web API**
```python
## Example #10
print("\nTest #10")
## do not save to file
todo = Arkivist()

# fetch from web api - invalid
todo.fetch("https://www.google.com")
# fetch from web api - valid
todo.fetch("https://jsonplaceholder.typicode.com/todos/1")
print("Show: ", todo.show())
```

**11. Check if empty or not**
```python
print("\nTest #11")
## do not save to file
people = Arkivist("test.json").clear()
print("Count:", people.count(), "; Is empty: ", people.is_empty())

# flattens nested dictionary
people.update({"dog": {"name": "Doggy"}})
print("Count:", people.count(), "; Is not empty: ", people.is_not_empty())
```

**12. Yield items**
```python
print("\nTest #12")
people = Arkivist("test.json").clear()

people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.update({"juan": {"name": "Juan"}})
people.update({"ufo": {"name": "UFO"}})
people.update({"xyz": {"name": "xyz"}})

# Get key value pairs
print("\nAll items:")
for key, value in people.items():
    print(key, value)

# Get key value pairs in reverse order
print("\nReverse:")
for key, value in people.items(sort=True, reverse=True):
    print(key, value)
```

**13. Querying**
```python
print("\nTest #13")
people = Arkivist("tests.json").clear()

people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.update({"juan": {"name": "Juan"}})
people.update({"ufo": {"name": "UFO"}})
people.update({"xyz": {"name": "xyz"}})

matches = people.where("name", "Doggy").show()
print("\nShow matches equals to 'Doggy':\n", matches)

print("\nLoop over matches with 'D/doggy':")
for key, value in people.where("name", "doggy", case_sensitive=False).items():
    print(" ", key, value)

matches = people.where("name").contains("a").show()
print("\nShow matches with 'a':\n", matches)

matches = people.where("name").contains("a", case_sensitive=False).show()
print("\nShow matches with 'A/a':\n", matches)

print("\nLoop over matches with 'A/a'")
for key, value in people.where("name").contains("a", case_sensitive=False).items():
    print(" ", key, value)

matches = people.where("name").exclude("a").show()
print("\nShow excluding with 'a':\n", matches)

matches = people.where("name").exclude("a", case_sensitive=False).show()
print("\nShow excluding with 'A/a':\n", matches)

print("\nLoop over matches excluding 'A/a':")
for key, value in people.where("name").exclude("a", case_sensitive=False).items():
    print(" ", key, value)
```