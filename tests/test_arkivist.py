"""Test suite for Arkivist.

Run with either:
    python -m unittest discover -s tests -v
    python -m pytest tests -v
"""

import json
import os
import shutil
import tempfile
import threading
import unittest
import warnings

from arkivist import Arkivist, ArkivistException

try:
    import cryptography  # noqa: F401

    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class ArkivistTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="arkivist-tests-")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def path(self, name):
        return os.path.join(self.tempdir, name)

    def read_raw(self, name):
        with open(self.path(name), "r", encoding="utf-8") as f:
            return f.read()


class TestBasics(ArkivistTestCase):
    def test_in_memory(self):
        data = Arkivist({"hello": "world"})
        self.assertEqual(data["hello"], "world")
        self.assertIsNone(data.filepath)

    def test_init_writes_initial_data(self):
        Arkivist({"a": 1}, filepath=self.path("init.json"), mode="w+")
        self.assertEqual(json.loads(self.read_raw("init.json")), {"a": 1})

    def test_init_filepath_keyword_only(self):
        Arkivist(filepath=self.path("kw.json")).set("x", 1)
        self.assertEqual(json.loads(self.read_raw("kw.json")), {"x": 1})

    def test_mode_r_missing_file_raises(self):
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("missing.json"), mode="r")

    def test_invalid_mode_raises(self):
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("x.json"), mode="a")

    def test_invalid_extension_raises(self):
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("data.txt"))

    def test_non_object_root_raises(self):
        with open(self.path("list.json"), "w", encoding="utf-8") as f:
            f.write("[1, 2, 3]")
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("list.json"))

    def test_corrupted_json_raises(self):
        with open(self.path("bad.json"), "w", encoding="utf-8") as f:
            f.write("{not valid json")
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("bad.json"))

    def test_set_get_roundtrip_and_persistence(self):
        storage = Arkivist(self.path("store.json"))
        storage.set("one", 1).set("two", 2)
        again = Arkivist(self.path("store.json"))
        self.assertEqual(again.get("one"), 1)
        self.assertEqual(again.get("two"), 2)
        self.assertEqual(again.get("three", "default"), "default")

    def test_w_plus_starts_fresh(self):
        Arkivist(self.path("fresh.json")).set("old", True)
        fresh = Arkivist(self.path("fresh.json"), mode="w+")
        self.assertTrue(fresh.is_empty())
        self.assertEqual(json.loads(self.read_raw("fresh.json")), {})


class TestDictConsistency(ArkivistTestCase):
    """Native dict mutations must persist like Arkivist methods do."""

    def test_update_persists(self):
        storage = Arkivist(self.path("u.json"))
        storage.update({"a": 1, "b": 2})
        self.assertEqual(json.loads(self.read_raw("u.json")), {"a": 1, "b": 2})

    def test_delete_persists(self):
        storage = Arkivist(self.path("d.json"))
        storage.update({"a": 1, "b": 2})
        del storage["a"]
        self.assertEqual(json.loads(self.read_raw("d.json")), {"b": 2})

    def test_pop_persists(self):
        storage = Arkivist(self.path("p.json"))
        storage.update({"a": 1, "b": 2})
        self.assertEqual(storage.pop("a"), 1)
        self.assertEqual(storage.pop("zzz", "fallback"), "fallback")
        self.assertEqual(json.loads(self.read_raw("p.json")), {"b": 2})

    def test_popitem_persists(self):
        storage = Arkivist(self.path("pi.json"))
        storage.set("only", 1)
        self.assertEqual(storage.popitem(), ("only", 1))
        self.assertEqual(json.loads(self.read_raw("pi.json")), {})

    def test_setdefault_persists(self):
        storage = Arkivist(self.path("sd.json"))
        storage.setdefault("a", 5)
        storage.setdefault("a", 99)
        self.assertEqual(json.loads(self.read_raw("sd.json")), {"a": 5})

    def test_clear_persists(self):
        storage = Arkivist(self.path("c.json"))
        storage.set("a", 1)
        storage.clear()
        self.assertEqual(json.loads(self.read_raw("c.json")), {})

    def test_missing_getitem_returns_none(self):
        # legacy Arkivist behavior, kept for backward compatibility
        storage = Arkivist({"a": 1})
        self.assertIsNone(storage["missing"])


class TestFindParentState(ArkivistTestCase):
    def test_find_set_get(self):
        names = Arkivist(self.path("names.json"))
        names.set("names", {})
        names.find("names").set("maria", 1)
        self.assertEqual(names.find("names").get("maria", 0), 1)
        self.assertEqual(names.find("names").get("pedro", 0), 0)

    def test_parent_resets_after_get(self):
        storage = Arkivist({"group": {"inner": 1}, "top": 2})
        self.assertEqual(storage.find("group").get("inner"), 1)
        # regression: parent must not leak into the next plain get()
        self.assertEqual(storage.get("top"), 2)

    def test_parent_resets_after_append_in(self):
        storage = Arkivist({"group": {}, "colors": ["red"]})
        storage.find("group").append_in("nums", 1)
        storage.append_in("colors", "blue")
        self.assertEqual(storage["colors"], ["red", "blue"])
        self.assertEqual(storage["group"]["nums"], [1])

    def test_non_dict_parent_raises(self):
        storage = Arkivist({"scalar": 5})
        with self.assertRaises(ArkivistException):
            storage.find("scalar").set("x", 1)
        # and the parent marker must have been cleared by the failure
        storage.set("y", 2)
        self.assertEqual(storage["y"], 2)


class TestListHelpers(ArkivistTestCase):
    def test_append_unique_sorted(self):
        test = Arkivist(self.path("lists.json"))
        test.append_in("colors", "red")
        test.append_in("colors", "orange")
        test.append_in("colors", ("blue", "orange"), unique=True, sort=True)
        self.assertEqual(test["colors"], ["blue", "orange", "red"])

    def test_remove_preserves_order(self):
        test = Arkivist({"colors": ["red", "green", "blue", "yellow"]})
        test.remove_in("colors", ("green", "purple"))
        self.assertEqual(test["colors"], ["red", "blue", "yellow"])

    def test_remove_scalar(self):
        test = Arkivist({"nums": [1, 2, 3]})
        test.remove_in("nums", 2)
        self.assertEqual(test["nums"], [1, 3])


class TestQueries(ArkivistTestCase):
    def sample(self):
        return Arkivist(
            {
                "abc": {"name": "Abc"},
                "dog": {"name": "Doggy"},
                "juan": {"name": "Juan"},
            }
        )

    def test_where_exact(self):
        names = self.sample()
        result = names.where("name", "Abc", exact=True).show()
        self.assertEqual(list(result), ["abc"])

    def test_where_substring_insensitive(self):
        names = self.sample()
        result = names.where("name", "a", exact=False, sensitivity=False).show()
        self.assertEqual(sorted(result), ["abc", "juan"])

    def test_exclude(self):
        names = self.sample()
        result = names.where("name").exclude("Abc").show()
        self.assertEqual(sorted(result), ["dog", "juan"])

    def test_query_generator_and_state_reset(self):
        names = self.sample()
        matches = dict(names.where("name", "Juan").query())
        self.assertEqual(list(matches), ["juan"])
        # query state must be fully cleared afterwards
        self.assertEqual(len(names.show()), 3)

    def test_where_on_non_string_values(self):
        data = Arkivist({"a": {"age": 30}, "b": {"age": "thirty"}})
        result = data.where("age", 30, exact=False).show()
        self.assertEqual(list(result), ["a"])

    def test_show_sorted(self):
        names = self.sample()
        self.assertEqual(list(names.show(sort=True, reverse=True)), ["juan", "dog", "abc"])

    def test_string_and_to_json(self):
        names = self.sample()
        self.assertEqual(json.loads(names.string()), dict(self.sample()))
        pretty = names.to_json(indent=2)
        self.assertIn("\n", pretty)
        self.assertEqual(json.loads(pretty), dict(self.sample()))


class TestTransformations(ArkivistTestCase):
    def test_flatten(self):
        data = Arkivist({"a": {"b": [1, 2]}, "c": 3})
        self.assertEqual(data.flatten(), {"a.b.0": 1, "a.b.1": 2, "c": 3})

    def test_invert(self):
        data = Arkivist({"a": 1, "b": 2})
        data.invert()
        self.assertEqual(dict(data), {1: "a", 2: "b"})

    def test_invert_unhashable_raises_and_preserves(self):
        data = Arkivist({"a": [1, 2]})
        with self.assertRaises(ArkivistException):
            data.invert()
        self.assertEqual(dict(data), {"a": [1, 2]})

    def test_load_dict_and_string(self):
        data = Arkivist({"old": True})
        data.load({"new": 1})
        self.assertEqual(dict(data), {"new": 1})
        data.load('{"newer": 2}')
        self.assertEqual(dict(data), {"newer": 2})

    def test_load_invalid_raises_and_preserves(self):
        data = Arkivist({"keep": True})
        with self.assertRaises(ArkivistException):
            data.load("{invalid json")
        with self.assertRaises(ArkivistException):
            data.load(12345)
        self.assertEqual(dict(data), {"keep": True})

    def test_random(self):
        self.assertEqual(Arkivist({}).random(), {})
        pair = Arkivist({"only": 1}).random()
        self.assertEqual(pair, {"only": 1})

    def test_matches(self):
        data = Arkivist({"one": 1})
        self.assertTrue(data.matches("one", 1))
        self.assertFalse(data.matches("one", 2))
        self.assertFalse(data.matches("two", 1))

    def test_reload(self):
        storage = Arkivist(self.path("r.json"))
        storage.set("a", 1)
        with open(self.path("r.json"), "w", encoding="utf-8") as f:
            f.write('{"external": true}')
        storage.reload()
        self.assertEqual(dict(storage), {"external": True})


class TestSaving(ArkivistTestCase):
    def test_autosave_off_requires_save(self):
        storage = Arkivist(self.path("manual.json"), autosave=False)
        storage.set("a", 1)
        self.assertEqual(json.loads(self.read_raw("manual.json")), {})
        storage.save()
        self.assertEqual(json.loads(self.read_raw("manual.json")), {"a": 1})

    def test_save_as_is_a_copy(self):
        storage = Arkivist(self.path("orig.json"))
        storage.set("a", 1)
        storage.save(save_as=self.path("copy.json"))
        storage.set("b", 2)
        # regression: save_as must not redirect subsequent autosaves
        self.assertEqual(json.loads(self.read_raw("copy.json")), {"a": 1})
        self.assertEqual(json.loads(self.read_raw("orig.json")), {"a": 1, "b": 2})

    def test_autosort(self):
        storage = Arkivist(self.path("sorted.json"), autosort=True)
        storage.set("b", 2)
        storage.set("a", 1)
        self.assertEqual(list(json.loads(self.read_raw("sorted.json"))), ["a", "b"])

    def test_indent(self):
        storage = Arkivist(self.path("indented.json"), indent=2)
        storage.set("a", 1)
        self.assertIn('\n  "a": 1', self.read_raw("indented.json"))

    def test_batch_saves_once_at_exit(self):
        storage = Arkivist(self.path("batch.json"))
        with storage.batch():
            for i in range(50):
                storage.set(str(i), i)
            self.assertEqual(json.loads(self.read_raw("batch.json")), {})
        self.assertEqual(len(json.loads(self.read_raw("batch.json"))), 50)
        self.assertTrue(storage.autosave)

    def test_context_manager_saves_on_exit(self):
        with Arkivist(self.path("ctx.json"), autosave=False) as storage:
            storage.set("a", 1)
        self.assertEqual(json.loads(self.read_raw("ctx.json")), {"a": 1})

    def test_no_leftover_temp_files(self):
        storage = Arkivist(self.path("tmpcheck.json"))
        for i in range(10):
            storage.set(str(i), i)
        leftovers = [n for n in os.listdir(self.tempdir) if n.endswith(".tmp")]
        self.assertEqual(leftovers, [])


class TestDeprecations(ArkivistTestCase):
    def test_count_warns_but_works(self):
        data = Arkivist({"a": 1, "b": 2})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(data.count(), 2)
        self.assertTrue(any(w.category is DeprecationWarning for w in caught))

    def test_doublecheck_warns_but_works(self):
        data = Arkivist({"one": 1})
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertTrue(data.doublecheck("one", 1))
            self.assertFalse(data.doublecheck("one", 2))
        self.assertTrue(any(w.category is DeprecationWarning for w in caught))

    def test_legacy_kwargs_warn(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Arkivist({"a": 1}, sort=True)
        self.assertTrue(any(w.category is DeprecationWarning for w in caught))


@unittest.skipUnless(HAS_CRYPTOGRAPHY, "cryptography is not installed")
class TestEncryption(ArkivistTestCase):
    def test_encrypt_roundtrip(self):
        authfile = self.path("secret-key.txt")
        storage = Arkivist(self.path("enc.json"), authfile=authfile)
        storage.encrypt()
        storage.set("weather", {})
        storage.find("weather").set("2022-04-14", "Cloudy")

        raw = json.loads(self.read_raw("enc.json"))
        self.assertEqual(raw.get("encryption"), "fernet")
        self.assertNotIn("Cloudy", self.read_raw("enc.json"))

        # regression: encrypted payload must contain the actual data
        again = Arkivist(self.path("enc.json"), authfile=authfile)
        self.assertEqual(again.find("weather").get("2022-04-14"), "Cloudy")

    def test_encrypt_does_not_overwrite_existing_key(self):
        authfile = self.path("stable-key.txt")
        storage = Arkivist(self.path("enc2.json"), authfile=authfile)
        storage.encrypt()
        with open(authfile, "r", encoding="utf-8") as f:
            key_before = f.read()
        storage.encrypt(False)
        storage.encrypt(True)
        with open(authfile, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), key_before)

    def test_decrypt_restores_plain_file(self):
        authfile = self.path("key3.txt")
        storage = Arkivist(self.path("enc3.json"), authfile=authfile)
        storage.encrypt()
        storage.set("a", 1)
        storage.encrypt(False)
        self.assertEqual(json.loads(self.read_raw("enc3.json")), {"a": 1})

    def test_encrypted_file_without_authfile_raises(self):
        authfile = self.path("key4.txt")
        storage = Arkivist(self.path("enc4.json"), authfile=authfile)
        storage.encrypt()
        storage.set("a", 1)
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("enc4.json"))

    def test_wrong_key_raises(self):
        storage = Arkivist(self.path("enc5.json"), authfile=self.path("key5.txt"))
        storage.encrypt()
        storage.set("a", 1)
        other = Arkivist(self.path("other.json"), authfile=self.path("key6.txt"))
        other.encrypt()
        with self.assertRaises(ArkivistException):
            Arkivist(self.path("enc5.json"), authfile=self.path("key6.txt"))


class TestThreadStress(ArkivistTestCase):
    def test_concurrent_writes(self):
        storage = Arkivist(self.path("stress.json"))
        workers, per_worker = 8, 50
        errors = []

        def work(worker):
            try:
                for i in range(per_worker):
                    storage.set(f"{worker}-{i}", i)
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=work, args=(w,)) for w in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(storage), workers * per_worker)
        # the file on disk must be valid JSON with every key present
        ondisk = json.loads(self.read_raw("stress.json"))
        self.assertEqual(len(ondisk), workers * per_worker)

    def test_concurrent_mixed_operations(self):
        storage = Arkivist(self.path("mixed.json"))
        for i in range(100):
            storage.set(f"seed-{i}", i)
        errors = []

        def writer():
            try:
                for i in range(50):
                    storage.set(f"w-{i}", i)
                    storage.append_in("shared", i)
            except Exception as e:  # pragma: no cover
                errors.append(e)

        def reader():
            try:
                for _ in range(50):
                    storage.show()
                    storage.random()
                    dict(storage.where("missing", "x").query())
            except Exception as e:  # pragma: no cover
                errors.append(e)

        threads = [threading.Thread(target=writer) for _ in range(4)]
        threads += [threading.Thread(target=reader) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        json.loads(self.read_raw("mixed.json"))


if __name__ == "__main__":
    unittest.main()
