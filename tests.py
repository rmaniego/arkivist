from arkivist import Arkivist

print("\nTest #0 New file")
dataset = Arkivist("temp/00-new.json", mode="w+")
print("Empty JSON file:", dataset)


print("\nTest #0 Valid file")
dataset = Arkivist("temp/00-valid1.json")

print("\nTest #0 Valid file")
dataset = Arkivist("temp/00-valid2.json")

print("\nTest #0 Invalid files")
try:
    dataset = Arkivist("temp/00-invalid1.json")
except Exception as e:
    print(str(e))

print("\nTest #0 Invalid files")
try:
    dataset = Arkivist("temp/00-invalid2.json")
except Exception as e:
    print(str(e))

print("\nTest #0 Invalid files")
try:
    dataset = Arkivist("temp/00-invalid3.json")
except Exception as e:
    print(str(e))

print("\nTest #0 Invalid files")
try:
    dataset = Arkivist("temp/00-invalid4.json")
except Exception as e:
    print(str(e))

print("\nTest #1 Initialization")
dataset = Arkivist("temp/01-initialization.json")
print("Empty JSON file:", dataset)

## Example #2 / autosave = True (default)
print("\nTest #2 Sorting")
people = Arkivist("temp/02-sorting.json")

person = {}
person.update({"name": "Ñino"})
people.update({"ñino": person})

people.set("boy", {"name": "Boy"})
people.set("girl", {"name": "Girl"})

print("Show all items (unsorted): ", people.show())
print("Show all items (sorted): ", people.show(sort=True))
print("Show all items (reverse): ", people.show(sort=True, reverse=True))

## Example #3 / autosave = False
print("\nTest #3 Manual Saving")
people = Arkivist("temp/03-manual-save.json", autosave=False)
person = {}
person.update({"name": "Maria"})
people.update({"maria": person})
people.save()
people.save(save_as="temp/03-save-as.json")

## Example #4
print("\nTest #4 Counter")
people = Arkivist("temp/04-counter.json")
people.set("juan", "Juan dela Cruz")
people.set("pedro", "Pedro delos Santos")
people.set("maria", "Maria Sta. Maria")
print("Count: ", people.count())

## Example #5
print("\nTest #5 Access Keys and Values")
people = Arkivist("temp/05-keys-values.json")
people.set("juan", "Juan dela Cruz")
people.set("pedro", "Pedro delos Santos")
people.set("maria", "Maria Sta. Maria")
# get the keys and values
print("Keys: ", list(people.keys()))
print("Values: ", list(people.values()))

## Example #6
print("\nTest #6 Invert Hashable key-value pairs")
simple = Arkivist("temp/06-invert.json")
simple.update({0: "a"})
simple.update({1: "b"})
simple.update({2: "c"})
print("Normal: ", simple.show())
simple.invert()
print("Invert: ", simple.show())

## Example #7
print("\nTest #7 Load (replace) and Clear old data")
people = Arkivist("temp/07-load-clear.json")
people.set("juan", "Juan dela Cruz")
people.set("pedro", "Pedro delos Santos")
people.set("maria", "Maria Sta. Maria")
print("Old: ", people.show())
alien = {"anon": {"name": "Anon"}}
people.load(alien)
print("New: ", people.show())
people.reset()
print("Cleared: ", people.show())

## Example #8
print("\nTest #8 Load from valid JSON string and Python dictionary.")
people = Arkivist("temp/08-load-valid.json")
# valid dictionary
people.load({"ufo": {"name": "UFO"}})
print("Valid Dictionary: ", people.show())
# valid string
people.load('{"dog": {"name": "Doggy"}}')
print("Valid String: ", people.show())
# flush invalid input
people.load(1234)
print("Invalid input: ", people.show())

## Example #9
print("\nTest #9 Flattener")
pets = Arkivist("temp/09-flattener.json")
pets.set("dog", {"breeds": ["Akita", "Golden Retriever"]})
pets.set("cat", {"patterns": ["Calico", "Tabby", "Tortoise Shell"]})
pets.set("ufo", {"outer-space": {"proxima centauri": [1, 2, 3]}})
print("Flatten: ", pets.flatten())

## Example #10
print("\nTest #10 Fetch from JSON API")
todo = Arkivist("temp/10-fetch.json")
todo.fetch("https://www.google.com")
todo.fetch("https://jsonplaceholder.typicode.com/todos/1", noerror=False)
print("Show: ", todo.show())

## Example #11
print("\nTest #11 Check if Empty")
# Check if empty
people = Arkivist("temp/11-is-empty.json")
people.set("juan", "Juan dela Cruz")
people.set("pedro", "Pedro delos Santos")
people.set("maria", "Maria Sta. Maria")
print("Count:", people.count(), "; Is empty: ", people.is_empty())

## Example #12
print("\nTest #12 Use native update function")
people = Arkivist("temp/12-update.json").reset()
people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.update({"juan": {"name": "Juan"}})
people.update({"ufo": {"name": "UFO"}})
people.update({"xyz": {"name": "xyz"}})

## Example #13
print("\nTest #13")
people = Arkivist("temp/13-queries.json").reset()
people.set("abc", {"name": "Abc"})
people.set("dog1", {"name": "Doggy"})
people.set("dog2", {"name": "doggy"})
people.set("juan", {"name": "Juan"})
people.set("ufo", {"name": "UFO"})
people.set("xyz", {"name": "xyz"})

matches = people.where("name", "Doggy").show()
print("\nShow all items where name is exactly 'Doggy':\n ", matches)

print("\nLoop over all items where name is 'doggy' or 'Doggy':")
for key, value in people.where("name", "doggy", sensitivity=False).query():
    print(" - ", key, value)

matches = people.where("name", "a", exact=False).show()
print("\nShow all items where name contains 'a':\n ", matches)

matches = people.where("name", "a", exact=False, sensitivity=False).show()
print("\nShow all items where name contains 'A/a':\n ", matches)

print("\nLoop over all items where name contains 'A/a'")
for key, value in people.where("name", "a", exact=False, sensitivity=False).query():
    print(" - ", key, value)

matches = people.where("name").exclude("a", exact=False).show()
print("\nShow all items excluding names those containing 'a':\n ", matches)

matches = people.where("name").exclude("a", exact=False, sensitivity=False).show()
print("\nShow all items excluding names those containing 'A/a':\n ", matches)

print("\nLoop over matches excluding names containing 'A/a':")
for key, value in (
    people.where("name").exclude("a", exact=False, sensitivity=False).query()
):
    print(" - ", key, value)

## Example #14
print("\nTest #14 Manual Save and Reload")
people = Arkivist("temp/14-reload.json", autosave=True).reset()

people.update({"abc": {"name": "Abc"}})
people.update({"dog": {"name": "Doggy"}})
people.save()

people.update({"juan": {"name": "Juan"}})
people.update({"ufo": {"name": "UFO"}})
people.update({"xyz": {"name": "xyz"}})
print("People:")
for key, value in people.items():
    print(" - ", key, value)

people.reload()
print("\nPeople:")
for key, value in people.items():
    print(" - ", key, value)

## Example #15
print("\nTest #15 Display as String")
hello = Arkivist("temp/15-string.json", indent=2)
hello.set("message", "Hello, world!")
print("Dictionary:", hello.show())
print("String:", hello.string())

## Example #16
print("\nTest #16 Get random item")
names = Arkivist("temp/16-random.json").reset()
names.update({"abc": {"name": "Abc"}})
names.update({"dog": {"name": "Doggy"}})
names.update({"juan": {"name": "Juan"}})
names.update({"xyz": {"name": "Xyz"}})
print("Random item:", people.random())

## Example #17
print("\nTest #17 Doublecheck expected value")
test = Arkivist("temp/17-doublecheck.json").reset()
test.set("number", 100)
print(" - Doublecheck (100):", test.doublecheck("number", 100))
print(" - Doublecheck (101):", test.doublecheck("number", 101))

## Example #18
print("\nTest #18 Find parent, set/get child")
test = Arkivist("temp/18-find-in.json").reset()
test.set("names", {})
test.find("names").set("juan", 14)
test.find("names").set("maria", 15)
test.find("names").set("pedro", 16)
print("Juan:", test.find("names").get("juan"))

## Example #19
print("\nTest #19 Append in (lists child)")
test = Arkivist("temp/19-append-in.json").reset()

test.append_in("colors", "red")
test.append_in("colors", "orange")
test.append_in("colors", "yellow")
test.append_in("colors", ("blue", "green"), unique=True, sort=True)
test.remove_in("colors", "yellow")
test.remove_in("colors", ("blue", "purple"))

test.set("numbers", {})
test.find("numbers").append_in("odd", 1)
test.find("numbers").append_in("odd", (1, 3, 5, [7]))
print(" - Lists:", test.show())

## Example #20
print("\nTest #20 Encryption (Fernet)")
weather = Arkivist("temp/20-weather.json", authfile="temp/2a-arkivist-auth.txt")
weather.set("weather", {})
weather.find("weather").set("2022-04-14", "Cloudy")
weather.find("weather").set("2022-04-15", "Sunny")
weather.encrypt()
weather.save("temp/20-weather-encrypted.json")
weather.encrypt(False)
weather.find("weather").set("2022-04-16", "Hazy")
weather.save()

weather = Arkivist("temp/20-encrypted.json", authfile="temp/20b-secret-key.txt")
weather.encrypt()
weather.set("weather", {})
weather.find("weather").set("2022-04-14", "Cloudy")
weather.find("weather").set("2022-04-15", "Sunny")
weather.find("weather").set("2022-04-16", "Hazy")
print("Weather:")
for key, value in weather["weather"].items():
    print(" - ", key, value)

## Example #21
print("\nTest #21a Check unexpected clearing of JSON file")
test = Arkivist("temp/21-mackaroo1.json")
print(" - Show:", test.show())

print("\nTest #21b Check unexpected clearing of JSON file (encrypted)")
test = Arkivist("temp/21-mackaroo2.json", authfile="temp/21-mackaroo2-auth.txt")
print(" - Show:", test.show())
