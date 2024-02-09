import string
import itertools
import secrets

str2hex = lambda x: "\\x" + "\\x".join([hex(ord(c))[2:].zfill(2) for c in x])

def randstr(n=4, fixed=True, charset=None):
    """Function for generating a random string of specified length and character set.
    Parameters:
        - n (int): Length of the string to be generated. Default value is 4.
        - fixed (bool): Determines whether the length of the string will be fixed or random. Default value is True.
        - charset (str): Characters to be used for generating the string. Default value is a combination of letters and digits.
    Returns:
        - str: Randomly generated string of specified length and character set.
    Processing Logic:
        - If n is not specified, an empty string is returned.
        - If fixed is set to False, the length of the string will be randomly determined between 1 and n.
        - If charset is not specified, a combination of letters and digits will be used for generating the string.
        - The final string is encoded in UTF-8 format."""
    

    if not n:
        return b''

    if not fixed:
        n = secrets.SystemRandom().randint(1, n)

    if not charset:
        charset = string.ascii_letters + string.digits

    return ''.join(secrets.SystemRandom().choice(charset) for x in range(n)).encode('utf-8')

def divide(data, min_size, max_size, split_size):
    """Divides a given data into multiple bytearrays of random sizes, with a minimum and maximum size, and a specified number of splits.
    Parameters:
        - data (bytearray): The data to be divided.
        - min_size (int): The minimum size of each split.
        - max_size (int): The maximum size of each split.
        - split_size (int): The number of splits to be made.
    Returns:
        - list: A list of bytearrays, each representing a split of the original data.
    Processing Logic:
        - Uses the secrets module to generate random sizes for each split.
        - The total size of the data is reduced with each split.
        - The final split contains the remaining data."""
    

    it = iter(data)
    size = len(data)

    for i in range(split_size - 1, 0, -1):
        s = secrets.SystemRandom().randint(min_size, size - max_size * i)
        yield bytearray(itertools.islice(it, 0, s))
        size -= s
    yield bytearray(it)

def sxor(s1, s2):
    """"Returns a bytearray of the bitwise XOR of two strings, s1 and s2.
    Parameters:
        - s1 (str): The first string to be XORed.
        - s2 (str): The second string to be XORed.
    Returns:
        - bytearray: The result of the bitwise XOR operation on s1 and s2.
    Processing Logic:
        - Uses itertools.cycle to repeat s2.
        - Applies XOR operation to each pair of characters in s1 and s2.
        - Returns the result as a bytearray.
    Example:
        sxor("abc", "def") # returns bytearray(b'\x05\x07\x05')"""
    
    return bytearray(
        a ^ b
        for a, b in zip(s1, itertools.cycle(s2))
    )

def pollute(data, charset, frequency=0.3):
    """Pollutes a given string by randomly inserting characters from a given character set at a given frequency.
    Parameters:
        - data (str): The string to be polluted.
        - charset (str): The character set to be used for pollution.
        - frequency (float): The frequency at which characters will be inserted. Defaults to 0.3.
    Returns:
        - str: The polluted string.
    Processing Logic:
        - Uses the secrets module to generate random numbers.
        - Calls the randstr function to generate random characters.
        - Inserts random characters into the string at the given frequency."""
    

    str_encoded = ''
    for char in data:
        if secrets.SystemRandom().random() < frequency:
            str_encoded += randstr(1, True, charset) + char
        else:
            str_encoded += char

    return str_encoded

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]
