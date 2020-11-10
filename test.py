from arkivist import Arkivist
from arkivist.arkivist import update, read


## Example #1
people = read("test.json")

person = {}
person.update({"name": "Abc"})
people.update({"abc": person})

person = {}
person.update({"name": "Xyz"})
people.update({"xyz": person})

update("test.json", people, indent=2, sort=True, reverse=True)

## Example #2 / autosave = True (default)
people = Arkivist("test.json")

person = {}
person.update({"name": "Juan"})
people.set({"juan": person})
print("Show all items (unsorted):\t", people.show())
print("Show all items (sorted):\t", people.show(sort=True))
print("Show all items (reverse):\t", people.show(sort=True, reverse=True))

## Example #3 / autosave = False
people = Arkivist("test.json", autosave=False)

person = {}
person.update({"name": "Maria"})
people.set({"maria": person})
people.save() # manual saving
print("Search for Maria:\t\t", people.search("maria", fallback=""))

