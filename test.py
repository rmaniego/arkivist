from arkivist import Arkivist
from arkivist.arkivist import update_file, read


## Example #1
print("\nTest #1")
people = read("test.json")

person = {}
person.update({"name": "Abc"})
people.update({"abc": person})

person = {}
person.update({"name": "Xyz"})
people.update({"xyz": person})

update_file("test.json", people, indent=2, sort=True, reverse=True)

## Example #2 / autosave = True (default)
print("\nTest #2")
people = Arkivist("test.json")

person = {}
person.update({"name": "Juan"})
people.set({"juan": person})
print("Show all items (unsorted): ", people.show())
print("Show all items (sorted): ", people.show(sort=True))
print("Show all items (reverse): ", people.show(sort=True, reverse=True))

## Example #3 / autosave = False
print("\nTest #3")
people = Arkivist("test.json", autosave=False)

person = {}
person.update({"name": "Maria"})
people.set({"maria": person})
people.save() # manual saving
people.save(filepath="test.backup.json") # save to another file
print("Search for Maria: ", people.search("maria", fallback=""))

## Example #4
print("\nTest #4")
people = Arkivist("test.json")

# print the number of entries
print("Count: ", people.count())

## Example #5
print("\nTest #5")
people = Arkivist("test.json")

# get the keys and values
print("Keys: ", people.keys())
print("Values: ", people.values())

## Example #6
print("\nTest #6")
simple = Arkivist("test.simple.json")

simple.clear()
simple.set({0: "a"})
simple.set({1: "b"})
simple.set({2: "c"})

# inverts the dictionary
print("Normal: ", simple.show())
simple.invert()
print("Invert: ", simple.show())

## Example #7
print("\nTest #7")
people = Arkivist("test.json")

# print original contents
print("Old: ", people.show())

# print new contents
alien = {"anon": {"name": "Anon"}}
people.replace(alien)
print("New: ", people.show())

# print empty dictionary
people.clear()
print("Clear: ", people.show())

## Example #8
print("\nTest #8")
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

## Example #9
print("\nTest #9")
people = Arkivist("test.json")

# flattens nested dictionary
people.set({"dog": {"name": "Doggy"}})
people.set({"ufo": {"name": "UFO"}})
print("Flatten: ", people.flatten().show())

## Example #10
print("\nTest #10")
## do not save to file
todo = Arkivist()

# fetch from web api - invalid
todo.fetch("https://www.google.com")
# fetch from web api - valid
todo.fetch("https://jsonplaceholder.typicode.com/todos/1")
print("Show: ", todo.show())


## Example #11
print("\nTest #11")
## do not save to file
people = Arkivist("test.json").clear()
print("Count:", people.count(), "; Is empty: ", people.is_empty())

# flattens nested dictionary
people.update({"dog": {"name": "Doggy"}})
print("Count:", people.count(), "; Is not empty: ", people.is_not_empty())
