from arkivist import Arkivist


## Example #2 / autosave = True (default)
print("\nTest #2")
people = Arkivist("tests.json") #, encoder="utf-8")

person = {}
person.update({"name": "Ñino"})
people.update({"ñino": person})

people.set("boy", {"name": "Boy"})
people.set("girl", {"name": "Girl"})

print("Show all items (unsorted): ", people.show())
print("Show all items (sorted): ", people.show(sort=True))
print("Show all items (reverse): ", people.show(sort=True, reverse=True))



## Example #3 / autosave = False
print("\nTest #3")
people = Arkivist("tests.json", autosave=False)

person = {}
person.update({"name": "Maria"})
people.update({"maria": person})
people.save() # manual saving
people.save(filepath="test.backup.json") # save to another file

## Example #4
print("\nTest #4")
people = Arkivist("tests.json")

# print the number of entries
print("Count: ", people.count())

## Example #5
print("\nTest #5")
people = Arkivist("tests.json")

# get the keys and values
print("Keys: ", people.keys())
print("Values: ", people.values())

## Example #6
print("\nTest #6")
simple = Arkivist("test.simple.json")

simple.clear()
simple.update({0: "a"})
simple.update({1: "b"})
simple.update({2: "c"})

# inverts the dictionary
print("Normal: ", simple.show())
simple.invert()
print("Invert: ", simple.show())

## Example #7
print("\nTest #7")
people = Arkivist("tests.json")

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
people = Arkivist("tests.json")

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
people = Arkivist("tests.json")

# flattens nested dictionary
people.update({"dog": {"name": "Doggy"}})
people.update({"ufo": {"name": "UFO"}})
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
# Check if empty
people = Arkivist("tests.json").clear()
print("Count:", people.count(), "; Is empty: ", people.is_empty())

# Check if not empty
people.update({"dog": {"name": "Doggy"}})
print("Count:", people.count(), "; Is not empty: ", people.is_not_empty())


## Example #12
print("\nTest #12")
people = Arkivist("tests.json").clear()

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


## Example #13
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

## Example #13
print("\nTest #13")
people = Arkivist("tests.json").clear()

people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.update({"juan": {"name": "Juan"}})
people.update({"ufo": {"name": "UFO"}})
people.update({"xyz": {"name": "xyz"}})

print("All:", people.show())
people.pop("ufo")
print("No UFO:", people.show())

## Example #14
print("\nTest #14")
people1 = Arkivist("people.json").clear()
people2 = Arkivist("people.json").clear()

people1.update({"abc": {"name": "Abc"}})
people1.update({"dog": {"name": "Doggy"}})
people1.update({"juan": {"name": "Juan"}})
people1.update({"ufo": {"name": "UFO"}})
people1.update({"xyz": {"name": "xyz"}})

print("People1:", people1.show())
print("People2:", people2.show())
people2.reload()
print("People2", people2.show())

## Example #15
print("\nTest #15")
hello = Arkivist("hello.json")
hello.default("hello", "", "world")
hello.default("hello", "", "friend")
print("Reset defaults:", hello.show())

## Example #16
print("\nTest #16")
print("Dictionary:", hello.show())
print("String:", hello.string())

## Example #17
print("\nTest #17")
people = Arkivist("people.json").clear()
people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.update({"juan": {"name": "Juan"}})
print("Random item:", people.random())

## Example #18
print("\nTest #18")
test = Arkivist("tests.json").clear()
test.set("number", 100)
print("Doublecheck (100):", test.doublecheck("number", 100))
print("Doublecheck (101):", test.doublecheck("number", 101))

## Example #19
print("\nTest #19")
test = Arkivist("tests.json").clear()
test.set("number", [1, 2, 3, 4, 5])
print("Show list [1, 2, 3, 4, 5]:", test.show())
test.extend_list("number", [6, 7, 8, 9, 0])
print("Extend list [6, 7, 8, 9, 0]:", test.show())
test.extend_list("number", [1, 10], unique=True)
print("Extend unique list [1, 10]:", test.show())
test.extend_list("number", [12, 15], sort=True)
print("Extend multidimensional list [12, 15]:", test.show())
test.extend_list("number", [[1, 2], 15], sort=True)
print("Extend multidimensional list [[1, 2], 15]:", test.show())



