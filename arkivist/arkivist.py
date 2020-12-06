"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json
import requests

class Arkivist:
    def __init__(self, filepath="", indent=4, sort=False, reverse=False, autosave=True):
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
        """
        self.save_to_file = True
        self.filepath = filepath
        if filepath == "": self.save_to_file = False
        self.collection = read(filepath)
        self.indent = indent
        self.sort = sort
        self.reverse = reverse
        self.autosave = autosave
    
    def update(self, data):
        """
            Formats and saves the dictionary into a JSON file.
            ...
            Parameters
            ---
            data: dictionary
                dictionary object
        """
        self.collection.update(data)
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse)
        return self
    
    def set(self, data):
        """ Duplicate for update function. """
        return self.update(data)

    def fetch(self, url):
        """
            Get JSON data from a web API through HTTP/HTTPS GET method.
            ...
            Parameters
            ---
            url: str
                any valid URL string
        """
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
        if type(data) == dict:
            self.replace(data)
        elif type(data) == str:
            try:
                temp = json.loads(data)
                self.replace(temp)
            except:
                pass
        return self
    
    def invert(self):
        """ Inverts the dictionary """
        try:
            # hashable keys / values
            self.collection = dict(zip(self.collection.values(), self.collection.keys()))
            if self.autosave and self.save_to_file:
                update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse)
        except:
            pass
        return self
    
    def flatten(self):
        """  Flattens a nested dictionary. """
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
        if sort:
            self.collection = dict(sorted(self.collection.items(), reverse=reverse))
        return self.collection
    
    def search(self, key, fallback=None):
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
        return self.collection.get(key, fallback)
    
    def keys(self):
        """ Get all the keys of the ditionary """
        return list(self.collection.keys())
    
    def values(self):
        """ Get all the values of the ditionary """
        return list(self.collection.values())
    
    def count(self):
        """ Count the number of entries in the dictionary """
        return len(self.collection)
    
    def clear(self):
        """ Clears the dictionary """
        self.collection = {}
        if self.autosave and self.save_to_file:
            update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse)
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
        if type(collection) == dict:
            self.collection = collection
            if self.autosave and self.save_to_file:
                update_file(self.filepath, self.collection, self.indent, self.sort, self.reverse)
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
        self.save_to_file = True
        savepath = self.filepath
        if filepath != "": savepath = filepath
        if savepath == "": savepath = "arkivist.data.json"
        update_file(savepath, self.collection, self.indent, self.sort, self.reverse)
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

def update_file(filepath, data, indent=4, sort=False, reverse=False):
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
            with open(filepath, "w+") as file:
                file.write(json.dumps(data, indent=indent))
        except:
            pass

def read(filepath):
    """
        Read JSON file and converts to a Python dictionary.
        ...
        Parameters
        ---
        filepath: string
            path to the json file
    """
    try:
        with open(filepath, "r") as file:
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