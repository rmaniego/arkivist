from arkivist.arkivist import update, read

people = read("test.json")

person = {}
person.update({"name": "Abc"})
people.update({"abc": person})

person = {}
person.update({"name": "Xyz"})
people.update({"xyz": person})

update("test.json", people, indent=2, sort=True, reverse=True)