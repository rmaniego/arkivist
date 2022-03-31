![](/resources/banner.png)

# arkivist
Arkivist is Python Dictionary wrapper for JSON files.

Other behaviors are similar to native Python dictionaries, the tutorial below only covers add-on feature specific to Arkivist.

## Fun fact
Arkivist is a play on the word Archive, which means a collection of historical documents or records. Arkivist is like your digital librarian that manages your important data for a lightweight and organized data storage.

## Official Release
**Arkivist** can now be used on your Python projects through PyPi by running pip command on a Python-ready environment.

`pip install arkivist --upgrade`

Current version is 1.1.42, but more updates are coming soon. Installing it will also install required packages including *requests*.

This is compatible with Python 3.6+ and is already used in various personal projects.

## Use-cases
**1.** Need a lightweight data storage with zero application installations. 
**2.** The project is for personal or hobby with low number of users who simultaneously access the data storage. 
**3.** The project requires a data storage that has a fast learning curve due to resource or time constraints. 

## Usage
**1. Import Package**
```python
from arkivist import Arkivist
```

**2. Cast Python Dictionary to Arkivist object**
```python
message = Arkivist({"hello": "world"})

data = {"a": "Ant", "b": "Bug", "c": "Cat"}
animals = Arkivist(data, filepath="animals.json")
```

**3. Instantiate data from existing JSON file**
```python
storage = Arkivist("storage.json") # or "myStorage.json"
```

**4. Set JSON File indentation**
```python
# indent = 1, 2, 3, or 4
storage = Arkivist("storage.json", indent=2)
```

**5. Customize sorting options**
```python
storage = Arkivist("storage.json", autosort=True, reverse=False)
```

**6. Disable Autosave**
```python
storage = Arkivist("storage.json", autosave=False)
storage.save()
storage.save(filepath="storage-copy.json")
```

**7. Add new entry**
```python
places= Arkivist("data/places.json")
places.set(1, "Sun")
places.set(2, "Earth")
places.set(3, "Moon")

# native update format
people = Arkivist("data/people.json")
people.update({"juan": {"name": "Juan Dela Cruz"}})
people.update({"maria": {"name": "Maria Dela Cruz"}})
```

**8. Get dictionary object**
```python
places = Arkivist("data/places.json")
print(places.show())
```

**9. Generate JSON-compliant string**
```python
places = Arkivist("data/places.json")
print(places.string())
```

**10. Clear dictionary data**
```python
places = Arkivist("data/places.json", autosave=False)
places.reset()
```

**11. Replace all contents**
```python
# replace from a valid dictionary
people = Arkivist("data/people.json")
friends = {"friend": {"name": "Friend"}, "enemy": {"name": "Enemy"}}
people.load(friends)

# load from valid JSON string
anons = "{\"robot\": {\"name\": \"Robot\"}, \"ghost\": {\"name\": \"Ghost\"}}"
people.load(anons)
```

**12. Check if empty or not**
```python
## do not save to file
people = Arkivist("data/people.json").reset()
print("Count:", people.count(), "; Is empty: ", people.is_empty())
```

**13. Flatten the nested dictionary**
```python
people = Arkivist("data/people.json")
people.set("juan", {"name": "Juan Dela Cruz"})
people.set("maria", {"name": "Maria Dela Cruz"})
print(people.flatten())
```

**14. Fetch from a web API**
```python
todos = Arkivist() # autosave = False, data is only in memory
todos.fetch("https://jsonplaceholder.typicode.com/todos/1")
print(todos.show())
```

**15. Get random key-value pair**
```python
names = Arkivist("names.json").reset()
names.set("abc", {"name": "Abc"})
names.set("dog", {"name": "Doggy"})
names.set("juan", {"names": "Juan"})
print("Random item:", names.random())
```

**16. Double check if expected key value is correct**
```python
numbers = Arkivist("numbers.json").reset()
numbers.set("one": 1)
print("Doublecheck (1):", numbers.doublecheck("one", 1))
print("Doublecheck (2):", numbers.doublecheck("one", 2))
```

**16. Perform shallow queries**
```python
names = Arkivist("names.json")
names.set("abc", {"name": "Abc"})
names.set("dog", {"name": "Doggy"})
names.set("juan", {"name": "Juan"})

# exact match
for name, data in names.where("name", "Abc").query():
    print(name, data)

# search containing the substring
for name, data in names.where("name", "a", exact=False).query():
    print(name, data)

# search containing the substring, case sensitivity = False
for name, data in names.where("name", "a", exact=False, sensitivity=False).query():
    print(name, data)

# search excluding the exact keyword
for name, data in names.where("name").exclude("Abc").query():
    print(name, data)

# search excluding the items containing the keyword
for name, data in names.where("name").exclude("a", exact=False).query():
    print(name, data)

# search excluding the items containing the keyword, case sensitivity = False
for name, data in names.where("name").exclude("A", exact=False, sensitivity=False).query():
    print(name, data)
```

**17. Find child of parent**
```python
names = Arkivist("names.json").reset()
names.set("names", {})
names.find("names").set("maria", 1)
print("Maria:", names.find("names").get("maria", 0))
print("Pedro:", names.find("names").get("pedro", 0))
```

**18. Append/Extend list children**
```python
test = Arkivist("tests.json").reset()
test.appendIn("colors", "red")
test.appendIn("colors", ("blue", "green"))
test.set("numbers", {})
test.find("numbers").appendIn("odd", 1)
test.find("numbers").appendIn("odd", (1, 3, 5, [7]))
```

## Futures
Arkivist is an ongoing project and new features will be added in the future. In the future, it aims to add complex querying and also add a security layer to protect data from unauthorized access.

## Conclusion
Arkivist allows you to build your Python apps with a lightweight data storage, this can come handy especially when you are doing personal and hobby projects that handles simple data.