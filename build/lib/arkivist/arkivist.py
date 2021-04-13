"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json
import requests

class Arkivist:
    def __init__(self, filepath="", indent=4, sort=False, reverse=False, autosave=True, encoding="utf-8"):
        """
            Read and prepare the JSON/Dictionary object.
            ...
            Parameters
            ---
            filepath: string
                path to save the json file
            indent: integer
                number of spaces in an indent (1, 2, 3, 4)
            sort: boolean
                sorts the dictionary based on keys
            reverse: boolean
                sorts the dictionary in reverse
            autosave: boolean
                save dictionary to JSON file after every update
            save_to_file: boolean
                save dictionary to JSON file, else just keep in memory
            encoding: string
                file encoding
        """
        self.save_to_file = True
        self.filepath = filepath
        if filepath == "": self.save_to_file = False
        self.collection = read(filepath, encoding)
        self.indent = indent
        self.sort = sort
        self.reverse = reverse
        self.autosave = autosave
        self.encoding = encoding
        ## query
        self.operator = "="
        self.child_key = None
        self.child_val = None
        self.case_sensitive = True
        self.matches = {}
    
    def set(self, key, value):
        """
            Formats and saves the dictionary into a JSON file.
            ...
            Parameters
            ---
            key: unique hashable string
                the key of the entry
            value: string, integer, float
                the value of the entry
        """
        self.child_key = None
        self.collection.update({key: value})
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self
    
    def update(self, data):
        """
            Formats and saves the dictionary into a JSON file.
            ...
            Parameters
            ---
            data: dictionary
                dictionary object
        """
        self.child_key = None
        self.collection.update(data)
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self
    
    def default(self, key, old, new):
        """
            If key equals to old value, update to new value
            ...
            Parameters
            ---
            key: string, int
                any unique value
            old: any data type
                old value to check
            new: any data type
                new value to replace    
        """
        self.child_key = None
        if self.collection.get(key, old) == old:
            self.collection.update({key: new})
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self

    def fetch(self, url):
        """
            Get JSON data from a web API through HTTP/HTTPS GET method.
            ...
            Parameters
            ---
            url: str
                any valid URL string
        """
        self.child_key = None
        try:
            with requests.get(url) as source:
                self.collection = source.json()
        except:
            pass
        return self
    
    def load(self, data):
        """
            Replaces the existing dictionary with another specified dictionary,
            same as replace except that it also parses string.
            ...
            Parameters
            ---
            data: str / dict
                any valid string or dict object
        """
        self.child_key = None
        if type(data) == dict:
            self.replace(data)
        elif type(data) == str:
            try:
                temp = json.loads(data)
                self.replace(temp)
            except:
                pass
        return self
    
    def reload(self):
        """ Update dictionary from JSON file """
        self.collection = read(self.filepath)
        return self
    
    def pop(self, key):
        """
            Remove key-value from the dictionary
            ...
            Parameters
            ---
            key: str
                any valid string found in the dictionary
        """
        try:
            self.child_key = None
            self.collection.pop(key)
            if self.autosave and self.save_to_file:
                update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        except:
            pass
        return self
    
    def invert(self):
        """ Inverts the dictionary """
        self.child_key = None
        try:
            # hashable keys / values
            self.collection = dict(zip(self.collection.values(), self.collection.keys()))
            if self.autosave and self.save_to_file:
                update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        except:
            pass
        return self
    
    def flatten(self):
        """  Flattens a nested dictionary. """
        self.child_key = None
        self.collection = flattener(self.collection)
        return self
    
    def show(self, sort=False, reverse=False):
        """
            Return the dictionary object.
            ...
            Parameters
            ---
            sort: boolean
                sorts the dictionary based on keys
            reverse: boolean
                sorts the dictionary in reverse
        """
        self.sort = sort
        self.reverse = reverse
        self.matches = query(self.collection, self.child_key, self.child_val, self.operator, self.case_sensitive)
        self.child_key = None
        if sort:
            self.matches = dict(sorted(self.matches.items(), reverse=reverse))
        return self.matches
    
    def items(self, sort=False, reverse=False):
        """
            Generator for dictionary
            ...
            Parameters
            ---
            sort: boolean
                sorts the dictionary based on keys
            reverse: boolean
                sorts the dictionary in reverse
        """
        self.sort = sort
        self.reverse = reverse
        self.matches = query(self.collection, self.child_key, self.child_val, self.operator, self.case_sensitive)
        self.child_key = None
        if sort:
            self.matches = dict(sorted(self.matches.items(), reverse=reverse))
        for key, value in self.matches.items():
            yield key, value
    
    def get(self, key, fallback=None):
        """
            Gets the value of the search key from the  dictionary.
            ...
            Parameters
            ---
            key: string
                key found in the dictionary
            fallback: any
                any datatype to return when the key doesn't exist
                
        """
        self.child_key = None
        return self.collection.get(key, fallback)
    
    def search(self, key, fallback=None):
        """ Duplicate of get function """
        self.child_key = None
        print("Deprected function, use get() instead.")
        return self
    
    def where(self, child, value=None, case_sensitive=True):
        """
            Gets the value of the search key from the  dictionary.
            ...
            Parameters
            ---
            child: string
                child key found in the dictionary
            value: string, int, float
                value of the child key
            case_sensitive: boolean
                if search operation is case sensitive
                
        """
        self.operator = "="
        self.child_key = child
        self.child_val = value
        self.case_sensitive = case_sensitive
        self.matches = {}
        return self
    
    def contains(self, value, case_sensitive=True):
        """
            Gets the value of the search key from the  dictionary.
            ...
            Parameters
            ---
            value: string, int, float
                value of the child key
            case_sensitive: boolean
                if search operation is case sensitive
                
        """
        if self.child_key != None:
            self.operator = "%"
            self.child_val = value
            self.case_sensitive = case_sensitive
            self.matches = {}
        return self
    
    def exclude(self, value, case_sensitive=True):
        """
            Gets the value of the search key from the  dictionary.
            ...
            Parameters
            ---
            value: string, int, float
                value of the child key
            case_sensitive: boolean
                if search operation is case sensitive
                
        """
        if self.child_key != None:
            self.operator = "x"
            self.child_val = value
            self.case_sensitive = case_sensitive
            self.matches = {}
        return self
    
    def keys(self):
        """ Get all the keys of the ditionary """
        self.child_key = None
        return list(self.collection.keys())
    
    def values(self):
        """ Get all the values of the ditionary """
        self.child_key = None
        return list(self.collection.values())
    
    def is_empty(self):
        """ Check if dictionary is empty """
        self.child_key = None
        if len(self.collection) == 0:
            return True
        return False
    
    def is_not_empty(self):
        """ Check if dictionary is not empty """
        self.child_key = None
        if len(self.collection) == 0:
            return False
        return True
    
    def count(self):
        """ Count the number of entries in the dictionary """
        self.child_key = None
        return len(self.collection)
    
    def clear(self):
        """ Clears the dictionary """
        self.child_key = None
        self.collection = {}
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self
    
    def replace(self, collection):
        """
            Replaces the existing dictionary with another specified dictionary
            ...
            Parameters
            ---
            collection: dict
                a dictionary to replace the contents of the original dictionary
        """
        self.child_key = None
        if type(collection) == dict:
            self.collection = collection
            if self.autosave and self.save_to_file:
                update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self

    def save(self, filepath=""):
        """
            Save and formats the dictionary into a JSON file.
            Doesn't change the original filepath.
            If no filepath and savepath is set, write to fallback filepath.
            ...
            Parameters
            ---
            filepath: string
                any filepath, if empty defaults to previously set filepath
        """
        self.child_key = None
        self.save_to_file = True
        savepath = self.filepath
        if filepath != "": savepath = filepath
        if savepath == "": savepath = "arkivist.data.json"
        update_file(savepath, self.collection, self.indent, self.sort, self.reverse, self.encoding)
        return self

def flattener(data):
    """
        Flatten dictionary
        ...
        Parameters
        ---
        data: dictionary
            any valid dictionary
    """
    out = {}
    ## https://www.geeksforgeeks.org/flattening-json-objects-in-python/
    def flatten(x, name =''):
        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(data)
    return out

def query(collection, child_key, child_val, operator, case_sensitive):
    matches = {}
    if child_key == None:
        matches = collection
    else:
        for key, data in collection.items():
            value = data.get(child_key, "")
            if operator == "=":
                if case_sensitive:
                    if child_val == value:
                        matches.update({key: data})
                else:
                    if str(child_val).lower() == str(value).lower():
                        matches.update({key: data})
            elif operator == "%":
                if case_sensitive:
                    if child_val in value:
                        matches.update({key: data})
                else:
                    # if case sensitive is false, convert values to string
                    if str(child_val).lower() in str(value).lower():
                        matches.update({key: data})
            elif operator == "x":
                if case_sensitive:
                    if child_val not in value:
                        matches.update({key: data})
                else:
                    # if case sensitive is false, convert values to string
                    if str(child_val).lower() not in str(value).lower():
                        matches.update({key: data})
    return matches

def update_file(filepath, data, indent=4, sort=False, reverse=False, encoding="utf-8"):
    """
        Formats and saves the dictionary into a JSON file.
        ...
        Parameters
        ---
        filepath: string
            path to save the json file
        data: dictionary
            dictionary object
        indent: integer
            number of spaces in an indent (1, 2, 3, 4)
        sort: boolean
            sorts the dictionary based on keys
        reverse: boolean
            sorts the dictionary in reverse
    """
    if type(data) == dict:
        if sort:
            data = dict(sorted(data.items(), reverse=reverse))
        try:
            indent = get_int(indent, min=1, max=4)
            with open(filepath, "w+", encoding=encoding) as file:
                file.write(json.dumps(data, indent=indent, ensure_ascii=False))
        except Exception as e:
            print(e)
            pass

def read(filepath, encoding="utf-8"):
    """
        Read JSON file and converts to a Python dictionary.
        ...
        Parameters
        ---
        filepath: string
            path to the json file
    """
    try:
        with open(filepath, "r", encoding=encoding) as file:
            return json.loads(file.read())
    except:
        return {}

# utils
def get_int(string, min=0, max=99999):
    """
        Converts a string into an integer with an optional min and max range.
        ...
        Parameters
        ---
        string: string
            a numeric string
        min: integer
            a number less than or equal to the requested number
        max: array, list, tuple, iterable (optional)
            a number greater than or equal to the requested number
    """
    try:
        number = int(str(string))
        if int(min) <= number <= int(max):
            return number
        return min
    except:
        return min