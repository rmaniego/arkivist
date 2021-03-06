![](/resources/banner.png)

# arkivist
Arkivist is a lightweight python package that simplifies the management of JSON data and files. It leverages the power of Python dictionaries and JSON files, by creating a persistent storage with less complexity.

## TL;DR
**Arkivist** is a lightweight python package that simplifies the management of JSON data and files. It leverages the power of Python dictionaries and JSON files, by creating a persistent storage with less complexity.

## Fun fact
Arkivist is a play on the word Archive, which means a collection of historical documents or records. Arkivist is like your digital librarian that manages your important data for a lightweight and organized data storage.

## Official Release
**Arkivist** can now be used on your Python projects through PyPi by running pip command on a Python-ready environment.

`pip install arkivist --upgrade`

Current version is 1.0.16, but more updates are coming soon. Installing it will also install required packages including *requests*.

This is compatible with Python 3.6+ and is already used in various personal projects.

## Use-cases
**1.** Need a lightweight data storage with zero application installations.
**2.** The project is for personal or hobby with low number of users who simultaneously access the data storage.
**3.** The project requires something that has a fast learning curve due to resource or time constraints.

## Usage
**1. Import Package**
```python
from arkivist import Arkivist
```

**2. Instantiate JSON file**
```python
# straightforward usage
json_data = Arkivist("myStorage.json")
```

**3. Add new entry**
```python
# basic add entry
places= Arkivist("data/places.json")
places.set(1, "Sun")
places.set(2, "Earth")
places.set(3, "Moon")
print(places.show())

# json update format
people = Arkivist("data/people.json")
people.update({"juan": {"name": "Juan Dela Cruz"}})
people.update({"maria": {"name": "Maria Dela Cruz"}})
print(people.show())
```

**4. Invert the key-value pairs**
This swaps the key and value of all the entries in the dictionary, key-value pairs must be hashable.
```python
places = Arkivist("data/places.json")
places.invert()
print(places.show())
```

**5. Get all data, reload from JSON file**
```python
places1 = Arkivist("data/places.json")
places2 = Arkivist("data/places.json")

print(places1.show())
print(places1.show(sorted=True))
print(places1.show(sorted=True, reverse=True))

places1.set(4, "Mars")
print(places1.show())
print(places2.show())
places2.reload() # reload updates
print(places2.show())
```

**6. Remove item / Clear all data**
```python
places = Arkivist("data/places.json", autosave=False)

# clear
places.clear()
print(places.show())

# populate
places.set(1, "Sun")
places.set(2, "Earth")
places.set(3, "Moon")

print("All:", places.show())
places.pop(1) # remove item
print("No Sun:", places.show())
```

**7. Manual save to file**
```python
people = Arkivist("data/people.json", autosave=False)
people.set("boy", {"name": "Boy"})
people.set("girl", {"name": "Girl"})
people.save()

# save to another file
people.set("ufo", {"name": "UFO"})
people.save(filepath="people_and_other_creatures.json")
```

**8. Replace all contents**
```python
# replace from a valid dictionary and replaces previous contents
people = Arkivist("data/people.json")
friends = {"friend": {"name": "Friend"}, "enemy": {"name": "Enemy"}}
people.replace(friends)
print(people.show())

# load from valid JSON string and replaces previous contents
anons = "{\"robot\": {\"name\": \"Robot\"}, \"ghost\": {\"name\": \"Ghost\"}}"
people.load(anons)
print(people.show())
```

**9. Flatten the nested dictionary**
```python
people = Arkivist("data/people.json")
people.set("juan", {"name": "Juan Dela Cruz"})
people.set("maria", {"name": "Maria Dela Cruz"})
people.flatten()
print(people.show())
```

**10. Fetch from a web API**
```python
todos = Arkivist() # autosave = False, data is only in memory
todos.fetch("https://jsonplaceholder.typicode.com/todos/1")
print(todos.show())
```

**11. Check if empty or not**
```python
## do not save to file
people = Arkivist("data/people.json").clear()
print("Count:", people.count(), "; Is empty: ", people.is_empty())

# add new content
people.update({"dog": {"name": "Doggy"}})
print("Count:", people.count(), "; Is not empty: ", people.is_not_empty())
```

**12. Yield items, use in for loop**
```python
people = Arkivist("data/people.json")
people.set("abc", {"name": "Abc"})
people.set("dog", {"name": "Doggy"})
people.set("juan", {"name": "Juan"})
people.set("ufo", {"name": "UFO"})
people.set("xyz", {"name": "xyz"})

# get key value pairs
print("\nAll items:")
for key, value in people.items():
    print(key, value)

# get key value pairs in reverse order
print("\nReverse:")
for key, value in people.items(sort=True, reverse=True):
    print(key, value)
```

**13. Querying**
```python
people = Arkivist("tests.json").clear()

people.set("abc", {"name": "Abc"})
people.set("dog", {"name": "Doggy"})
people.set("juan", {"name": "Juan"})
people.set("ufo", {"name": "UFO"})
people.set("xyz", {"name": "xyz"})

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

**14. Setting Defaults**
```python
hello = Arkivist("hello.json")
hello.default("hello", "", "world")
hello.default("hello", "", "friend")
print("Test", hello.show())
```

**15. Get raw string**
```python
hello = Arkivist("hello.json")
hello.default("hello", "", "world")
hello.default("hello", "", "friend")
print("Test", hello.string())
```

**16. Get random key-value pair**
```python
people = Arkivist("people.json").clear()
people.set("abc", {"name": "Abc"})
people.set("dog", {"name": "Doggy"})
people.set("juan", {"name": "Juan"})
print("Random item:", people.random())
```

**17. Double check if expected key value is correct**
```python
numbers = Arkivist("numbers.json").clear()
numbers.set("one": 1)
print("Doublecheck (1):", numbers.doucblecheck("one", 1))
print("Doublecheck (2):", numbers.doucblecheck("one", 2))
```

## Futures
Arkivist is an ongoing project and new features will be added in the future. In the future, it aims to add complex querying and also add a security layer to protect data from unauthorized access.

## Conclusion
Arkivist allows you to build your Python apps with a lightweight data storage, this can come handy especially when you are doing personal and hobby projects that handles simple data.