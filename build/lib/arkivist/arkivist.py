"""
    (c) 2020 Rodney Maniego Jr.
    Arkivist
"""
import json


def update(filepath, data, indent=4, sort=False, reverse=False):
    """
        Save and formats dictionary into a JSON file.
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